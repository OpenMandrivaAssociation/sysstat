%define	debug_package	%nil

Name: 		sysstat
Version: 	11.3.1
Release: 	1
Summary: 	Includes the sar and iostat system monitoring commands
License: 	GPLv2
Group: 		Monitoring
URL: 		http://pagesperso-orange.fr/sebastien.godard/
Source0: 	http://pagesperso-orange.fr/sebastien.godard/%{name}-%{version}.tar.xz
Patch0:		sysstat-10.1.2-fix-format-errors.patch
BuildRequires:	pkgconfig(systemd)

%description
This package provides the sar and iostat commands for the Linux
operating system, similar to their traditional UNIX counterparts.
They enable system monitoring of disk, network, and other IO activity.

%prep
%setup -q
%patch0 -p1 -b .strfmt
iconv -f windows-1252 -t utf8 CREDITS > CREDITS.aux
mv CREDITS.aux CREDITS

%build
%setup_compile_flags
export sa_lib_dir=%{_libdir}/sa
%configure --enable-debuginfo

make CFLAGS="%optflags" \
	PREFIX="%{_prefix}" \
	SA_LIB_DIR="%{_libdir}/sa" \
	MAN_DIR="%{_mandir}"


%install
make MAN_DIR=%{_mandir} IGNORE_MAN_GROUP=y PREFIX=%{_prefix} DESTDIR=%{buildroot}  SA_LIB_DIR=%{_libdir}/sa install

# Install service file
mkdir -p %{buildroot}%{_unitdir}
install -m 0644 sysstat.service %{buildroot}%{_unitdir}/

rm -fr %{buildroot}%{_datadir}/doc/%{name}-%{version}
mkdir -p %{buildroot}/etc/{cron.daily,cron.hourly}

cat > %{buildroot}/etc/cron.daily/%name <<EOF
#!/bin/sh

# generate a daily summary of process accounting.
%_libdir/sa/sa2 -A &

EOF
chmod +x  %{buildroot}/etc/cron.daily/%name

cat > %{buildroot}/etc/cron.hourly/%name <<EOF
#!/bin/sh

# snapshot system usage every 10 minutes six times.
%_libdir/sa/sa1 600 6 &

EOF
chmod +x  %{buildroot}/etc/cron.hourly/%name

rm -fr %{buildroot}%_prefix/doc

%find_lang %{name}

%post
%_post_service %{name}

%preun
%_preun_service %{name}

if [[ $1 -eq 0 ]]; then
  # Remove sa logs if removing sysstat completely
  rm -f %{_localstatedir}/log/sa/*
fi

%files -f %{name}.lang
%doc CHANGES COPYING CREDITS FAQ
%config(noreplace) %{_sysconfdir}/cron.hourly/sysstat
%config(noreplace) %{_sysconfdir}/cron.daily/sysstat
%config(noreplace) %{_sysconfdir}/sysconfig/sysstat.ioconf
%config(noreplace) %{_sysconfdir}/sysconfig/sysstat
%{_unitdir}/sysstat.service
%{_bindir}/*
%{_libdir}/sa
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man8/*
/var/log/sa
