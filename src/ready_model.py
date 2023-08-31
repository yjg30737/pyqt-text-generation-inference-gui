import subprocess
import re
import psutil

# using cmd
def ready_model_func(model='bigscience/bloom-560m',
                     num_shard=1,
                     volume='%cd%\data',
                     token=None):
    try:
        token = token if token else None
        command = f'''
                docker run --gpus all --shm-size 1g -e HUGGING_FACE_HUB_TOKEN={token} -p 8080:80 -v {volume}:/data ghcr.io/huggingface/text-generation-inference:latest --model-id {model} --num-shard {num_shard}
                '''

        subprocess.Popen(command.split(), shell=True)
    except Exception as e:
        print(e)

# docker: Error response from daemon: driver failed programming external connectivity on endpoint vigorous_greider (f71457a9a24a6349126083680fcc4d6af68678789e9e0a3d6af7546f08ab4afa): Bind for 0.0.0.0:8080 failed: port is already allocated.

if __name__ == '__main__':
    ready_model_func()