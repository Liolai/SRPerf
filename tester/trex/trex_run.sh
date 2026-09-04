
TREX_YAML_FILE_CONFIG=/etc/trex_cfg.yaml

if  [ ! -f "${TREX_YAML_FILE_CONFIG}" ]; then
	cp ./trex_cfg.yaml "${TREX_YAML_FILE_CONFIG}"
	echo "${TREX_YAML_FILE_CONFIG} will be created using the default one..."
fi

if pgrep -f "t-rex-64" > /dev/null; then
	sudo kill $(pgrep -f "t-rex-64")
fi
sh -c "cd /opt/trex-core-3.08 && sudo nohup ./t-rex-64 -i -c $(($(nproc) - 2)) --iom 0 > /tmp/trex.log 2>&1 &" > /dev/null
