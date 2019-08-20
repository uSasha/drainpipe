import os
import random
import sys
import time

import pandas as pd
import redis

help_message = 'Hello, please pass pattern to match and path to CSV file to dump.'


class StreamDumper:
    def __init__(self, redis, pattern, log_path, consumer_group='default', consumer_name='default'):
        self.redis = redis
        self.pattern = pattern
        self.log_path = log_path
        self.stream_cursor = dict()
        self.consumer_group = consumer_group
        self.consumer_name = consumer_name

        try:
            with open(self.log_path, 'r') as f:
                self.header = [word for word in f.readline().strip().split(',') if word]
        except FileNotFoundError:
            self.header = []

    @staticmethod
    def find_header(stream_content):
        columns = [column.decode() for column in stream_content[0][1][0][1].keys()]
        if columns:
            return ['stream', 'timestamp'] + columns
        else:
            return []

    def consume_streams(self):
        _, streams = self.redis.scan(match=self.pattern, count=int(10e10))  # somehow None option don't work
        for stream in streams:
            if stream not in self.stream_cursor:
                try:
                    self.stream_cursor[stream] = '>'
                    self.redis.xgroup_create(stream, self.consumer_group)
                except redis.exceptions.ResponseError:
                    pass
        if not self.stream_cursor:
            return

        result = self.redis.xreadgroup(self.consumer_group, self.consumer_name, self.stream_cursor, noack=True)
        if not self.header and result:
            self.header = self.find_header(result)
            with open(self.log_path, 'w') as f:
                f.write(','.join(self.header) + '\n')

        for stream, content in result:
            df = pd.DataFrame(content, columns=['timestamp', 'content'])
            df['timestamp'] = df['timestamp'].apply(lambda t: int(t.decode().split('-')[0]) // 1000)
            df['stream'] = stream.decode()

            for column in self.header:
                if column not in ['stream', 'timestamp']:
                    df[column] = df['content'].apply(lambda c: c.get(column.encode(), b'').decode())

            df[self.header].to_csv(self.log_path, mode='a', index=False, header=None)


if __name__ == '__main__':
    try:
        _, pattern, file_name = sys.argv
    except ValueError:
        print(help_message)

    path_to_csv = f'data/{file_name}'
    redis_host = os.environ.get('redis_host') or 'localhost'
    redis_port = int(os.environ.get('redis_port') or 6379)
    idle_seconds = float(os.environ.get('idle_seconds') or 1)
    consumer_group = os.environ.get('consumer_group') or 'drainpipe'
    consumer_name = os.environ.get('HOSTNAME') or 'local'
    if 'linuxkit' in consumer_name:
        consumer_name = random.randint(0, 10e10)  # docker for mac

    cache = redis.Redis(redis_host, redis_port)
    drain = StreamDumper(cache, pattern, path_to_csv, consumer_group, consumer_name)

    while True:
        drain.consume_streams()
        time.sleep(idle_seconds)
