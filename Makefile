all: pyflightcontrol/proto/dolos_pb2.py

pyflightcontrol/proto/dolos_pb2.py: proto/pyflightcontrol.proto
	protoc --python_out=pyflightcontrol proto/pyflightcontrol.proto

clean:
	rm -f pyflightcontrol/proto/dolos_pb2.py
	find -name "*.pyc" -print0 | xargs -0 rm -f
