all: pyflightcontrol/proto/pyflightcontrol_pb2.py
install: stmp-install

pyflightcontrol/proto/pyflightcontrol_pb2.py: proto/pyflightcontrol.proto
	protoc --python_out=pyflightcontrol proto/pyflightcontrol.proto

stmp-install: pyflightcontrol/proto/pyflightcontrol_pb2.py
	python3 setup.py build
	python3 setup.py install
	touch stmp-install

install-base: stmp-install
	install -D liberation_mono.ttf -t /usr/local/share/pyflightcontrol/ -m 644

install-aircraft: stmp-install
	install -D service/*.service -t /etc/systemd/system/ -m 644
	systemctl daemon-reload

clean:
	rm -rf pyflightcontrol/proto/dolos_pb2.py stmp-install build
	find -name "*.pyc" -print0 | xargs -0 rm -f
