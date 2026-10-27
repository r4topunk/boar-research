#!/bin/bash
# Proxy offline check from the Mac: does the iPhone advertise its device service (mDNS _apple-mobdev2) on the Mac's Wi-Fi (en0)?
# USB-link interfaces (CoreDevice NCM) always show it. Cellular cannot be observed from the Mac; it rests on r4to's word.
WIFI=$(networksetup -listallhardwareports | awk '/Wi-Fi/{getline; print $2}')
IDX=$(python3 -c "import socket;print(socket.if_nametoindex('$WIFI'))")
OUT=$( (dns-sd -B _apple-mobdev2._tcp local. & P=$!; sleep 4; kill $P) 2>/dev/null | awk '/ Add /{print $4}' | sort -u | tr '\n' ' ')
if echo " $OUT " | grep -q " $IDX "; then echo "$(date +%T) NETCHECK: iPhone service SEEN on Wi-Fi ($WIFI idx $IDX; ifaces: $OUT) -> NOT offline"; exit 2
else echo "$(date +%T) NETCHECK: not on Wi-Fi ($WIFI idx $IDX); only on ifaces [$OUT] (USB link). Cellular: not observable"; fi
