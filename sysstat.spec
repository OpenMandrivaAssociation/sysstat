Name:		sysstat
Version:	10.0.5
Release:	1
Summary:	Includes the sar and iostat system monitoring commands
License:	GPLv2
Group:		System/Configuration/Other
URL:		http://pagesperso-orange.fr/sebastien.godard/
Source0:	http://pagesperso-orange.fr/sebastien.godard/%{name}-%{version}.tar.gz
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


%changelog
* Sat May 19 2012 Alexander Khrukin <akhrukin@mandriva.org> 10.0.5-1
+ Revision: 799586
- version update 10.0.5.

* Sat Mar 10 2012 Alexander Khrukin <akhrukin@mandriva.org> 10.0.4-1
+ Revision: 784006
- version update 10.0.4

* Wed Nov 30 2011 Alexander Khrukin <akhrukin@mandriva.org> 10.0.3-1
+ Revision: 735780
- version update 10.0.3

* Wed Dec 01 2010 Sandro Cazzaniga <kharec@mandriva.org> 9.6.1-1mdv2011.0
+ Revision: 604500
- fix version
- correct version
- update to 9.0.6.1

* Sun Jul 11 2010 Sandro Cazzaniga <kharec@mandriva.org> 9.1.3-1mdv2011.0
+ Revision: 551164
- fix source (use a tar.gz given by upstream)
- update to 9.1.3

* Sat Apr 24 2010 Sandro Cazzaniga <kharec@mandriva.org> 9.1.1-2mdv2010.1
+ Revision: 538440
- don't define {name version release} on top of spec.
- fix license to GPLv2 (according to COPYING file)
- use %%configure2_5x
- use 'rm -rf' in %%preun
- use {_sysconfdir} in %%files
- bump rel

  + trem <trem@mandriva.org>
    - update to 9.1.1

* Thu Nov 12 2009 Frederik Himpe <fhimpe@mandriva.org> 9.0.6-1mdv2010.1
+ Revision: 465205
- update to new version 9.0.6

* Wed Sep 23 2009 Frederik Himpe <fhimpe@mandriva.org> 9.0.5-1mdv2010.0
+ Revision: 447885
- update to new version 9.0.5

* Mon Jul 20 2009 Frederik Himpe <fhimpe@mandriva.org> 9.0.4-1mdv2010.0
+ Revision: 398230
- Update to new version 9.0.4

* Sun May 24 2009 Frederik Himpe <fhimpe@mandriva.org> 9.0.3-1mdv2010.0
+ Revision: 379246
- Update to new version 9.0.3

* Wed Mar 11 2009 Frederik Himpe <fhimpe@mandriva.org> 9.0.1-1mdv2009.1
+ Revision: 353925
- Update to new version 9.0.1
- Add patch fixing build with -Werror=format-security

* Sat Oct 11 2008 Frederik Himpe <fhimpe@mandriva.org> 8.1.6-1mdv2009.1
+ Revision: 291684
- update to new version 8.1.6

* Fri Aug 08 2008 Thierry Vignaud <tv@mandriva.org> 8.1.3-3mdv2009.0
+ Revision: 269402
- rebuild early 2009.0 package (before pixel changes)

* Wed Jun 11 2008 Olivier Thauvin <nanardon@mandriva.org> 8.1.3-2mdv2009.0
+ Revision: 218224
- fix path substitution, then fixing #41296

* Sun May 25 2008 trem <trem@mandriva.org> 8.1.3-1mdv2009.0
+ Revision: 211253
- 8.1.3

* Mon Feb 11 2008 Olivier Thauvin <nanardon@mandriva.org> 8.1.1-1mdv2008.1
+ Revision: 165159
- 8.1.1

* Wed Jan 16 2008 Thierry Vignaud <tv@mandriva.org> 7.1.6-3mdv2008.1
+ Revision: 153724
- remove useless kernel require
- kill re-definition of %%buildroot on Pixel's request

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Thu Aug 23 2007 Thierry Vignaud <tv@mandriva.org> 7.1.6-2mdv2008.0
+ Revision: 70353
- fileutils, sh-utils & textutils have been obsoleted by coreutils a long time ago

* Wed Aug 22 2007 Erwan Velu <erwan@mandriva.org> 7.1.6-1mdv2008.0
+ Revision: 69301
- 7.1.6

* Wed Jul 04 2007 Erwan Velu <erwan@mandriva.org> 7.1.5-1mdv2008.0
+ Revision: 48238
- 7.1.5

* Mon Apr 23 2007 Erwan Velu <erwan@mandriva.org> 7.1.3-1mdv2008.0
+ Revision: 17463
- 7.1.3

