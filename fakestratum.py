import asyncio
import json

# define all the methods that can be invoked
def mining_subscribe(id):
    return [
        f'{{"result":[[["mining.set_difficulty","731ec5e0649606ff"],["mining.notify","731ec5e0649606ff"]],"e9695791",4],"id":{id},"error":null}}',
        '{ “id”: null, “method”: “mining.set_difficulty”, “params”: [500]}',
        '{"params": ["1db7", "0b29bfff96c5dc08ee65e63d7b7bab431745b089ff0cf95b49a1631e1d2f9f31", "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff2503777d07062f503253482f0405b8c75208", "0b2f436f696e48756e74722f0000000001603f352a010000001976a914c633315d376c20a973a758f7422d67f7bfed9c5888ac00000000", ["f0dbca1ee1a9f6388d07d97c1ab0de0e41acdf2edac4b95780ba0a1ec14103b3", "8e43fd2988ac40c5d97702b7e5ccdf5b06d58f0e0d323f74dd5082232c1aedf7", "1177601320ac928b8c145d771dae78a3901a089fa4aca8def01cbff747355818", "9f64f3b0d9edddb14be6f71c3ac2e80455916e207ffc003316c6a515452aa7b4", "2d0b54af60fad4ae59ec02031f661d026f2bb95e2eeb1e6657a35036c017c595"], "00000002", "1b148272", "52c7b81a", true], "id": null, "method": "mining.notify"}'
    ]

def mining_authorize(id):
    return [
        f'{"id": {id}, "result": true, "error": null}'
    ]

def mining_configure(id):
    return [
        f'{"error": null, "id": {id}, "result": {"version-rolling": true, "version-rolling.mask": "1fffe000"}}'
    ]

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
        results = methods[method](id)
        for result in results:
            print(f"Sending: {result}")
            writer.write(result)
    else:
        response = json.dumps({
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            },
            "id": id_
        })
        writer.write(response.encode())

    await writer.drain()

    print("Closing the connection")
    writer.close()

async def main():
    server = await asyncio.start_server(handle_request, '0.0.0.0', 8888)

    async with server:
        await server.serve_forever()

asyncio.run(main())