#!/bin/bash

set -e

DOWNLOAD_DIR=/tmp/confu-deps

NINJA_DIR="$DOWNLOAD_DIR/ninja"
NINJA_URL="https://github.com/ninja-build/ninja/archive/v1.7.2.tar.gz"

CMAKE_DIR="$DOWNLOAD_DIR/cmake"
CMAKE_URL="https://cmake.org/files/v3.7/cmake-3.7.2.tar.gz"

LIBSSL_DIR="$DOWNLOAD_DIR/libssl"
LIBSSL_URL="https://www.openssl.org/source/openssl-1.0.2k.tar.gz"

LIBGIT2_DIR="$DOWNLOAD_DIR/libgit2"
LIBGIT2_URL="https://github.com/libgit2/libgit2/archive/v0.25.1.tar.gz"
LIBGIT2_LIB=libgit2.so.0.25.1
LIBGIT2_SONAME=libgit2.so.25

function install_ninja() {
	mkdir -p "$DOWNLOAD_DIR"
	if [ -f "$DOWNLOAD_DIR/ninja.tgz" ]
	then
		rm -f "$DOWNLOAD_DIR/ninja.tgz"
	fi
	wget "$NINJA_URL" -O "$DOWNLOAD_DIR/ninja.tgz"
	if [ -d "$NINJA_DIR" ]
	then
		rm -rf "$NINJA_DIR"
	fi
	mkdir -p "$NINJA_DIR"
	tar xf "$DOWNLOAD_DIR/ninja.tgz" -C "$NINJA_DIR" --strip-components=1
	pushd "$NINJA_DIR"
	python configure.py --bootstrap
	mkdir -p "$HOME/.local/bin"
	cp -f ninja "$HOME/.local/bin/ninja"
	popd
}

function build_cmake() {
	mkdir -p "$DOWNLOAD_DIR"
	if [ -f "$DOWNLOAD_DIR/cmake.tgz" ]
	then
		rm -f "$DOWNLOAD_DIR/cmake.tgz"
	fi
	wget "$CMAKE_URL" -O "$DOWNLOAD_DIR/cmake.tgz"
	if [ -d "$CMAKE_DIR" ]
	then
		rm -rf "$CMAKE_DIR"
	fi
	mkdir -p "$CMAKE_DIR"
	tar xf "$DOWNLOAD_DIR/cmake.tgz" -C "$CMAKE_DIR" --strip-components=1
	pushd "$CMAKE_DIR"
	./configure --prefix="$CMAKE_DIR/install" --parallel=$(nproc)
	make -j $(nproc)
	make install
	popd
}

function build_libssl() {
	mkdir -p "$DOWNLOAD_DIR"
	if [ -f "$DOWNLOAD_DIR/libssl.tgz" ]
	then
		rm -f "$DOWNLOAD_DIR/libssl.tgz"
	fi
	wget "$LIBSSL_URL" -O "$DOWNLOAD_DIR/libssl.tgz"
	if [ -d "$LIBSSL_DIR" ]
	then
		rm -rf "$LIBSSL_DIR"
	fi
	mkdir -p "$LIBSSL_DIR"
	tar xf "$DOWNLOAD_DIR/libssl.tgz" -C "$LIBSSL_DIR" --strip-components=1
	pushd "$LIBSSL_DIR"
	./config "--prefix=$LIBSSL_DIR/install" "--openssldir=$LIBSSL_DIR/install" no-shared no-asm -fPIC
	# Do not use -j option: libssl Makefile doesn't support parallel builds
	make
	make install
	popd
}

function build_libgit2() {
	mkdir -p "$DOWNLOAD_DIR"
	if [ -f "$DOWNLOAD_DIR/libgit2.tgz" ]
	then
		rm -f "$DOWNLOAD_DIR/libgit2.tgz"
	fi
	wget "$LIBGIT2_URL" -O "$DOWNLOAD_DIR/libgit2.tgz"
	if [ -d "$LIBGIT2_DIR" ]
	then
		rm -rf "$LIBGIT2_DIR"
	fi
	mkdir -p "$LIBGIT2_DIR"
	tar xf "$DOWNLOAD_DIR/libgit2.tgz" -C "$LIBGIT2_DIR" --strip-components=1
	mkdir -p "$LIBGIT2_DIR/build"
	pushd "$LIBGIT2_DIR/build"
	"$CMAKE_DIR/install/bin/cmake" -G Ninja \
		"-DCMAKE_LIBRARY_PATH=$LIBSSL_DIR/install/include:$LIBSSL_DIR/install/lib" \
		"-DCMAKE_INSTALL_PREFIX=$LIBGIT2_DIR/install" "-DCMAKE_MAKE_PROGRAM=$NINJA_DIR/ninja"  \
		-DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON -DBUILD_CLAR=OFF \
		"-DOPENSSL_ROOT_DIR=$LIBSSL_DIR/install" \
		"-DOPENSSL_SSL_LIBRARY=$LIBSSL_DIR/install/lib/libssl.a" \
		"-DOPENSSL_CRYPTO_LIBRARY=$LIBSSL_DIR/install/lib/libcrypto.a" ..
	"$HOME/.local/bin/ninja"
	"$HOME/.local/bin/ninja" install
	mkdir -p "$HOME/.local/lib"
	cp -f "$LIBGIT2_DIR/install/lib/$LIBGIT2_LIB" "$HOME/.local/lib/"
	ln -f -s "$HOME/.local/lib/$LIBGIT2_LIB" "$HOME/.local/lib/$LIBGIT2_SONAME"
	popd
}

function install_pygit2() {
	LIBGIT2="$LIBGIT2_DIR/install" LDFLAGS="-Wl,-rpath,$HOME/.local/lib,--enable-new-dtags" pip install --user --upgrade --ignore-installed --force-reinstall pygit2==0.25.0
	python -c "import pygit2"
}

function clean() {
	rm -rf "$DOWNLOAD_DIR"
}

function uninstall() {
	if [ "$(uname -s)" != "Darwin" ]
	then
		rm -f "$HOME/.local/bin/ninja"
		rm -f "$HOME/.local/lib/$LIBGIT2_LIB"
		unlink "$HOME/.local/lib/$LIBGIT2_SONAME"
	fi
}

if [ "$1" == "--uninstall" ]
then
	uninstall
else
	if [ "$(uname -s)" == "Darwin" ]
	then
		brew install libgit2 ninja
		pip install --user pygit2
	else
		install_ninja
		build_cmake
		build_libssl
		build_libgit2
		install_pygit2
		clean
	fi
fi
