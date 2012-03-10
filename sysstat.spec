Name: 		sysstat
Version: 	10.0.4
Release: 	1
Summary: 	Includes the sar and iostat system monitoring commands
License: 	GPLv2
Group: 		System/Configuration/Other
URL: 		http://pagesperso-orange.fr/sebastien.godard/
Source0: 	http://pagesperso-orange.fr/sebastien.godard/%{name}-%{version}.tar.gz
Patch0:		sysstat-10.0.3-strfmt.patch
Requires(preun): coreutils grep
Requires(postun): coreutils grep

%description
This package provides the sar and iostat commands for the Linux
operating system, similar to their traditional UNIX counterparts.
They enable system monitoring of disk, network, and other IO activity.

%prep
%setup -q
%patch0 -p1 -b .strfmt

%build
export sa_lib_dir=%{_libdir}/sa 
%configure2_5x 
make CFLAGS="$RPM_OPT_FLAGS" \
	PREFIX="%{_prefix}" \
	SA_LIB_DIR="%{_libdir}/sa" \
	MAN_DIR="%{_mandir}"


%install
make MAN_DIR=%{_mandir} IGNORE_MAN_GROUP=y PREFIX=%{_prefix} DESTDIR=%{buildroot}  SA_LIB_DIR=%{_libdir}/sa install

rm -fr %{buildroot}%{_datadir}/doc/%{name}-%{version}

mkdir -p %{buildroot}/etc/{cron.daily,cron.hourly}

cat > %{buildroot}/etc/cron.daily/%name <<EOF
#!/bin/sh

# generate a daily summary of process accounting.
%_libdir/sa/sa2 -A &

EOF

cat > %{buildroot}/etc/cron.hourly/%name <<EOF
#!/bin/sh

# snapshot system usage every 10 minutes six times.
%_libdir/sa/sa1 600 6 &

EOF

rm -fr %{buildroot}%_prefix/doc

%find_lang %{name}

%triggerpostun -- sysstat <= 3.3.3-1
# earlier versions of sysstat had crontabs done in a bad way.  fix it.
if [ `id -u` = "0" -a "$1" -ge "2" ]; then
  egrep -v 'sysstat|sa1|sa2' /etc/crontab > /tmp/crontab.$$
  mv /tmp/crontab.$$ /etc/crontab && chmod 644 /etc/crontab
fi

%preun
if [ "$1" = 0 ]; then
  # Remove sa logs if removing sysstat completely
  rm -rf /var/log/sa/*
fi

%files -f %{name}.lang
%defattr(-,root,root)
%attr(755,root,root) %config(noreplace) %{_sysconfdir}/cron.hourly/sysstat
%attr(755,root,root) %config(noreplace) %{_sysconfdir}/cron.daily/sysstat
%config(noreplace) %{_sysconfdir}/sysconfig/sysstat.ioconf
%config(noreplace) %{_sysconfdir}/sysconfig/sysstat
%{_bindir}/*
%{_libdir}/sa
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man8/*
/var/log/sa
