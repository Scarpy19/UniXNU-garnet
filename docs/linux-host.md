# Linux host build constraints

The upstream Linux installer in UniXNU revision `a74949b0d2fbfeb6936f9baee4e8e974c36c35fb` cannot be run unmodified while keeping writes inside this project: it requires root for installation, copies `xcrun`, `plutil`, and `codesign` shims into `/usr/bin`, and uses `/var/tmp` unless `TMPDIR` is overridden. The install prefix alone does not prevent those writes. We have not run it.

The kernel driver also checks `/usr/bin/xcrun`; upstream's `plutil` shim documentation states that XNU makefiles use `/usr/bin/plutil` literally. Adding a project-local tool directory to `PATH` therefore does not by itself make the build work. The host compiler wrapper references `/usr/bin/ld` as a host tool; this is a separate dependency from writing files there. Linux kernel builds also need host compiler, libraries, headers and build utilities. Using existing host tools is not the same as an entirely self-contained toolchain.

Before attempting a local-prefix implementation, audit the pinned XNU makefiles and all absolute tool paths, then design changes that preserve upstream behavior. Set `TMPDIR` within the workspace, do not use `sudo`, and test both path resolution and write confinement. A probe, partial build or project-local adaptation is not evidence that the whole XNU kernel builds. Do not change the host system or install packages without separate user authorization.

Some userdata preparation paths still require macOS according to upstream documentation. Full firmware and kernel compilation remain unverified.
