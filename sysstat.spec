Name: 		sysstat
Version:	12.7.4
Release:	1
Summary: 	Includes the sar and iostat system monitoring commands
License: 	GPLv2
Group: 		Monitoring
URL: 		https://sysstat.github.io/
Source0: 	https://sysstat.github.io/sysstat-packages/%{name}-%{version}.tar.xz
BuildRequires:	systemd-rpm-macros
BuildRequires:	lm_sensors-devel
Requires:	xz
Requires:	findutils

%description
This package provides the sar and iostat commands for the Linux
operating system, similar to their traditional UNIX counterparts.
They enable system monitoring of disk, network, and other IO activity.

%prep
%autosetup -p1

%build
%configure \
	--enable-debuginfo \
	--enable-install-cron \
	--enable-copy-only \
	--disable-file-attr \
	--disable-stripping \
	--with-systemdsystemunitdir='%{_unitdir}' \
	--with-systemdsleepdir='%{_unitdir}-sleep' \
	sadc_options='-S DISK' \
	history=28 \
	compressafter=31

%make_build

%install
%make_install

rm -rf %{buildroot}%{_docdir}/%{name}-%{version}

%find_lang %{name}

%post
%systemd_post sysstat.service sysstat-collect.timer sysstat-summary.timer

%preun
%systemd_preun sysstat.service sysstat-collect.timer sysstat-summary.timer
if [ $1 -eq 0 ]; then
# Remove sa logs if removing sysstat completely
    rm -rf %{_localstatedir}/log/sa/*
fi

%postun
%systemd_postun sysstat.service sysstat-collect.timer sysstat-summary.timer

%files -f %{name}.lang
%license COPYING
%doc CHANGES CREDITS FAQ.md README.md
%config(noreplace) %{_sysconfdir}/sysconfig/sysstat
%config(noreplace) %{_sysconfdir}/sysconfig/sysstat.ioconf
%{_bindir}/*
%{_libdir}/sa
%{_unitdir}/sysstat*
%{_systemd_util_dir}/system-sleep/sysstat*
%doc %{_mandir}/man1/*
%doc %{_mandir}/man5/*
%doc %{_mandir}/man8/*
%{_localstatedir}/log/sa
