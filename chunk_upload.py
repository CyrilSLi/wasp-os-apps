from os import path
import subprocess

filename = "apts_data"
file = path.join(path.dirname(__file__), filename)

mode = "w"
wasptool_path = "tools/wasptool"
size = 160
chunks = (path.getsize(file) + size - 1) // size
chunk = 0

if input("Verify only? (Y/n) ").lower() != "y":
    with open(file, "r") as f:
        while True:
            data = f.read(size)
            chunk += 1
            if not data:
                break
            cmd = f"with open('{filename}', '{mode}') as f: f.write({data!r}); wasp.gc.collect()"
            print(f"Sending chunk {chunk}/{chunks}...")
            result = subprocess.run([wasptool_path, "--eval", cmd], check=True, capture_output=True, text=True)
            if any(str(len(data)) == line.strip() for line in result.stdout.splitlines()):
                print(f"Chunk of size {len(data)} written successfully")
            else:
                print("Error writing chunk:")
                print(result.stdout)
                print(result.stderr)
                print(cmd)
                break
            mode = "a"

hash_script = """\
{wasp_code}
fvn = 0xcbf29ce484222325
with open("{filename}", "rb") as f:
 while True:
  data = f.read(1)
  if not data: break
  fvn = ((fvn ^ data[0]) * 0x100000001b3) & 0xffffffffffffffff
print("{source} FNV1A_64A hash:", fvn)\
"""
exec(hash_script.format(filename=file, source="Local", wasp_code=""))
subprocess.run([wasptool_path, "--eval", hash_script.format(
    filename=filename,
    source="Remote",
    wasp_code="wasp.gc.collect()"
)], check=True)
