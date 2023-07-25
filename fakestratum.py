import asyncio
import json

# define all the methods that can be invoked
def mining_subscribe():
    return "pong"

def mining_authorize():
    return "pong"

def mining_configure():
    return "pong"

# map of function names to functions
methods = {
    'mining.subscribe': mining_subscribe,
    'mining.authorize': mining_authorize,
    'mining.configure': mining_configure,
}

async def handle_request(reader, writer):
    data = await reader.readline()
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print(f"Received {message} from {addr}")

    try:
        request = json.loads(message)
    except json.JSONDecodeError:
        print(f"Failed to decode JSON: {message}")
        return

    method = request.get("method")
    id_ = request.get("id")

    if method in methods:
        result = methods[method]()
        response = json.dumps({
            "jsonrpc": "2.0",
            "result": result,
            "id": id_
        })
    else:
        response = json.dumps({
            "jsonrpc": "2.0",
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            },
            "id": id_
        })

    print(f"Sending: {response}")
    writer.write(response.encode())
    await writer.drain()

    print("Closing the connection")
    writer.close()

async def main():
    server = await asyncio.start_server(handle_request, '0.0.0.0', 8888)

    async with server:
        await server.serve_forever()

asyncio.run(main())