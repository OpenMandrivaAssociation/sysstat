%define	name	sysstat
%define version 7.1.5
%define release %mkrel 1

Name: 		%name
Version: 	%version
Release: 	%release
Summary: 	Includes the sar and iostat system monitoring commands
License: 	GPL
Group: 		System/Configuration/Other
URL: 		http://perso.wanadoo.fr/sebastien.godard
Source: 	http://ibiblio.org/pub/Linux/system/status/%{name}-%{version}.tar.bz2
Requires: 	kernel >= 2.2.16-21
Requires(preun): sh-utils textutils grep fileutils
Requires(postun): sh-utils textutils grep fileutils
BuildRoot: 	%{_tmppath}/%{name}-root

%description
This package provides the sar and iostat commands for the Linux
operating system, similar to their traditional UNIX counterparts.
They enable system monitoring of disk, network, and other IO activity.

%prep
%setup -q

%build
%configure
make CFLAGS="$RPM_OPT_FLAGS" \
	PREFIX="%{_prefix}" \
	SA_LIB_DIR="%{_libdir}/sa" \
	MAN_DIR="%{_mandir}"


%install
rm -rf %{buildroot}
make MAN_DIR=%{_mandir} IGNORE_MAN_GROUP=y PREFIX=%{_prefix} DESTDIR=%{buildroot}  SA_LIB_DIR=%{_libdir}/sa install

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
  rm -f /var/log/sa/*
fi

%clean
rm -rf %{buildroot}

%files -f %{name}.lang
%defattr(-,root,root)
%doc CHANGES COPYING CREDITS README TODO sysstat-%version.lsm
%attr(755,root,root) %config(noreplace) /etc/cron.hourly/sysstat
%attr(755,root,root) %config(noreplace) /etc/cron.daily/sysstat
%config(noreplace) %{_sysconfdir}/sysconfig/sysstat.ioconf
%config(noreplace) %{_sysconfdir}/sysconfig/sysstat
%{_bindir}/*
%{_libdir}/sa
%{_mandir}/man1/*
%{_mandir}/man8/*
/var/log/sa
