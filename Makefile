all: pyflightcontrol/proto/pyflightcontrol_pb2.py

pyflightcontrol/proto/pyflightcontrol_pb2.py: proto/pyflightcontrol.proto
	protoc --python_out=pyflightcontrol proto/pyflightcontrol.proto

install: pyflightcontrol/proto/pyflightcontrol_pb2.py
	python3 setup.py build
	python3 setup.py install

install-base:
	install -D liberation_mono.ttf /usr/local/share/pyflightcontrol -m 644

install-aircraft:
	install -D service/*.service /etc/systemd/system -m 644
	systemctl daemon-reload

clean:
	rm -f pyflightcontrol/proto/dolos_pb2.py
	find -name "*.pyc" -print0 | xargs -0 rm -f
