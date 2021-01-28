import asyncio

import aioserial


async def read_and_print(aioserial_instance: aioserial.AioSerial):
    while True:
        data: bytes = await aioserial_instance.read_async()
        print(data.decode(errors='ignore'), end='', flush=True)
        if b'\n' in data:
            aioserial_instance.close()
            break

aioserial_instance: aioserial.AioSerial = aioserial.AioSerial(
    port='/dev/ttyUSB0', baudrate=115200)
asyncio.run(asyncio.gather(read_and_print(aioserial_instance),
                           aioserial_instance.write_async(b'Hello, World!\n')))
