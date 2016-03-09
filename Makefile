all: pyflightcontrol/proto.py

pyflightcontrol/proto/dolos_pb2.py: proto/dolos.proto
	protoc --python_out=pyflightcontrol proto/dolos.proto

clean:
	rm -f pyflightcontrol/proto/dolos_pb2.py
	find -name "*.pyc" -print0 | xargs -0 rm -f
