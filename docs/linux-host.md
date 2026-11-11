# Linux host build constraints

The upstream Linux installer in UniXNU revision `a74949b0d2fbfeb6936f9baee4e8e974c36c35fb` cannot be run unmodified while keeping writes inside this project: it requires root for installation, copies `xcrun`, `plutil`, and `codesign` shims into `/usr/bin`, and uses `/var/tmp` unless `TMPDIR` is overridden. The install prefix alone does not prevent those writes. We have not run it.

The kernel driver also checks `/usr/bin/xcrun`; upstream's `plutil` shim documentation states that XNU makefiles use `/usr/bin/plutil` literally. Adding a project-local tool directory to `PATH` therefore does not by itself make the build work. The host compiler wrapper references `/usr/bin/ld` as a host tool; this is a separate dependency from writing files there. Linux kernel builds also need host compiler, libraries, headers and build utilities. Using existing host tools is not the same as an entirely self-contained toolchain.

The user subsequently authorized compilation outside the project, package installation, and administrative access in WSL. A host dependency check reported `llvm-config missing`. Noninteractive `sudo` initially requested a password; after the user changed the configuration, `wsl -d Debian -u scarpy -- sudo -n true` succeeded. WSL root access was also verified. The upstream installer destinations `/usr/bin/xcrun`, `/usr/bin/plutil`, `/usr/bin/codesign`, and `/opt/unixnu-linux` did not exist before setup. The official installer has been started as WSL root with `--package-manager apt -j 4`; completion has not yet been confirmed. A probe, partial build or setup success is not evidence that the whole XNU kernel builds.

Some userdata preparation paths still require macOS according to upstream documentation. Full firmware and kernel compilation remain unverified.

The pinned `scripts/unixnu/kernel.py` Linux environment sets `UNIXNU_SDK_VERSION=17.0` and `DARWIN_TRIPLE=arm64-apple-ios17.0` even though this research configuration selects arm64e / iPadOS 27. Whether later commands override those values correctly has not been established; inspect the actual command lines before claiming that the Linux path supports this profile.
