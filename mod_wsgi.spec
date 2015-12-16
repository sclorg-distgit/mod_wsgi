%{?scl:%scl_package mod_wsgi}

%define use_python3 0

%if 0%{?scl:1}
%{!?_httpd24_apxs:       %{expand: %%global _httpd24_apxs       %%{_sbindir}/apxs}}
%{!?_httpd24_mmn:        %{expand: %%global _httpd24_mmn        %%(cat %{_includedir}/httpd/.mmn 2>/dev/null || echo missing-httpd-devel)}}
%{!?_httpd24_confdir:    %{expand: %%global _httpd24_confdir    %%{_sysconfdir}/httpd/conf.d}}
# /etc/httpd/conf.d with httpd < 2.4 and defined as /etc/httpd/conf.modules.d with httpd >= 2.4
%{!?_httpd24_modconfdir: %{expand: %%global _httpd24_modconfdir %%{_sysconfdir}/httpd/conf.d}}
%{!?_httpd24_moddir:    %{expand: %%global _httpd24_moddir    %%{_libdir}/httpd/modules}}
%else
%{!?_httpd_apxs:       %{expand: %%global _httpd_apxs       %%{_sbindir}/apxs}}
%{!?_httpd_mmn:        %{expand: %%global _httpd_mmn        %%(cat %{_includedir}/httpd/.mmn 2>/dev/null || echo missing-httpd-devel)}}
%{!?_httpd_confdir:    %{expand: %%global _httpd_confdir    %%{_sysconfdir}/httpd/conf.d}}
# /etc/httpd/conf.d with httpd < 2.4 and defined as /etc/httpd/conf.modules.d with httpd >= 2.4
%{!?_httpd_modconfdir: %{expand: %%global _httpd_modconfdir %%{_sysconfdir}/httpd/conf.d}}
%{!?_httpd_moddir:    %{expand: %%global _httpd_moddir    %%{_libdir}/httpd/modules}}
%endif

Name:           %{?scl:%scl_prefix}mod_wsgi
Version:        3.4
Release:        12.sc1%{?dist}
Summary:        A WSGI interface for Python web applications in Apache
Group:          System Environment/Libraries
License:        ASL 2.0
URL:            http://modwsgi.org
Source0:        http://modwsgi.googlecode.com/files/mod_wsgi-%{version}.tar.gz
Source1:        wsgi.conf
Patch0:         mod_wsgi-3.4-connsbh.patch
Patch1:         mod_wsgi-3.4-procexit.patch
Patch2:         mod_wsgi-3.4-coredump.patch
Patch3:         mod_wsgi-3.4-configure-python3.patch
Patch4:         mod_wsgi-3.4-CVE-2014-0240.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  %{?scl:httpd24-}httpd-devel, %{?scl:%scl_prefix}python-devel, autoconf
%if 0%{?scl:1}
Requires:       %{?scl:httpd24-}httpd-mmn = %{_httpd24_mmn}
%else
Requires:       %{?scl:httpd24-}httpd-mmn = %{_httpd_mmn}
%endif

# Suppress auto-provides for module DSO
%if 0%{?scl:1}
%{?filter_provides_in: %filter_provides_in %{_httpd24_moddir}/.*\.so$}
%else
%{?filter_provides_in: %filter_provides_in %{_httpd_moddir}/.*\.so$}
%endif
%{?filter_setup}

%description
The mod_wsgi adapter is an Apache module that provides a WSGI compliant
interface for hosting Python based web applications within Apache. The
adapter is written completely in C code against the Apache C runtime and
for hosting WSGI applications within Apache has a lower overhead than using
existing WSGI adapters for mod_python or CGI.


%prep
%setup -q -n mod_wsgi-%{version}
%patch0 -p1 -b .connsbh
%patch1 -p1 -b .procexit
%patch2 -p1 -b .coredump

%if %{use_python3}
%patch3 -p1 -b .python3
%endif

%patch4 -p1 -b .cve0240

%build
%if 0%{?scl:1}
. /opt/rh/httpd24/enable
. /opt/rh/%scl/enable

# Regenerate configure for -coredump patch change to configure.in
autoconf
export LDFLAGS="$RPM_LD_FLAGS -L%{_libdir}"
export CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing"
%configure --enable-shared --with-apxs="%{_httpd24_apxs} -Wl,'-R%{_libdir}'"
%else
# Regenerate configure for -coredump patch change to configure.in
autoconf
export LDFLAGS="$RPM_LD_FLAGS -L%{_libdir}"
export CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing"
%configure --enable-shared --with-apxs=%{_httpd_apxs}
%endif
make %{?_smp_mflags}



%install
rm -rf $RPM_BUILD_ROOT

%if 0%{?scl:1}
. /opt/rh/httpd24/enable
. /opt/rh/%scl/enable

make install DESTDIR=$RPM_BUILD_ROOT LIBEXECDIR=%{_httpd24_moddir}
install -d -m 755 $RPM_BUILD_ROOT%{_httpd24_modconfdir}
sed -e 's/mod_wsgi/mod_%{scl_prefix}wsgi/' %{SOURCE1} >modconf
install -p -m 644 modconf $RPM_BUILD_ROOT%{_httpd24_modconfdir}/10-%{scl_prefix}wsgi.conf
mv  $RPM_BUILD_ROOT%{_httpd24_moddir}/mod_wsgi.so \
    $RPM_BUILD_ROOT%{_httpd24_moddir}/mod_%{scl_prefix}wsgi.so

%else

make install DESTDIR=$RPM_BUILD_ROOT LIBEXECDIR=%{_httpd_moddir}

install -d -m 755 $RPM_BUILD_ROOT%{_httpd_modconfdir}
%if "%{_httpd_modconfdir}" == "%{_httpd_confdir}"
# httpd <= 2.2.x
install -p -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_httpd_confdir}/wsgi.conf
%else
# httpd >= 2.4.x
install -p -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_httpd_modconfdir}/10-wsgi.conf
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc LICENCE README
%if 0%{?scl:1}
%config(noreplace) %{_httpd24_modconfdir}/*.conf
%{_httpd24_moddir}/mod_%{scl_prefix}wsgi.so
%else
%config(noreplace) %{_httpd_modconfdir}/*.conf
%{_httpd_moddir}/mod_wsgi.so
%endif


%changelog
* Thu Jun 05 2014 Jan Kaluza <jkaluza@redhat.com> - 3.4.12
- fix for CVE-2014-0240 (#1104698)

* Mon Mar 24 2014 Jan Kaluza <jkaluza@redhat.com> - 3.4-11
- remove provides of internal library (#1075678)

* Mon Mar 24 2014 Jan Kaluza <jkaluza@redhat.com> - 3.4-10
- rename mod_wsgi.so to not conflict with other mod_wsgi collections (#1075678)

* Fri Nov 15 2013 Jan Kaluza <jkaluza@redhat.com> - 3.4-9
- use rpath for mod_wsgi.so

* Wed Oct 30 2013 Jan Kaluza <jkaluza@redhat.com> - 3.4-8
- support for software collections

* Tue Dec 11 2012 Jan Kaluza <jkaluza@redhat.com> - 3.4-7
- compile with -fno-strict-aliasing to workaround Python
  bug http://www.python.org/dev/peps/pep-3123/

* Thu Nov 22 2012 Joe Orton <jorton@redhat.com> - 3.4-6
- use _httpd_moddir macro

* Thu Nov 22 2012 Joe Orton <jorton@redhat.com> - 3.4-5
- spec file cleanups

* Wed Oct 17 2012 Joe Orton <jorton@redhat.com> - 3.4-4
- enable PR_SET_DUMPABLE in daemon process to enable core dumps

* Wed Oct 17 2012 Joe Orton <jorton@redhat.com> - 3.4-3
- use a NULL c->sbh pointer with httpd 2.4 (possible fix for #867276)
- add logging for unexpected daemon process loss

* Wed Oct 17 2012 Matthias Runge <mrunge@redhat.com> - 3.4-2
- also use RPM_LD_FLAGS for build bz. #867137

* Mon Oct 15 2012 Matthias Runge <mrunge@redhat.com> - 3.4-1
- update to upstream release 3.4

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jun 13 2012 Joe Orton <jorton@redhat.com> - 3.3-6
- add possible fix for daemon mode crash (#831701)

* Mon Mar 26 2012 Joe Orton <jorton@redhat.com> - 3.3-5
- move wsgi.conf to conf.modules.d

* Mon Mar 26 2012 Joe Orton <jorton@redhat.com> - 3.3-4
- rebuild for httpd 2.4

* Tue Mar 13 2012 Joe Orton <jorton@redhat.com> - 3.3-3
- prepare for httpd 2.4.x

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Nov 01 2011 James Bowes <jbowes@redhat.com> 3.3-1
- update to 3.3

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Jul 27 2010 David Malcolm <dmalcolm@redhat.com> - 3.2-2
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Tue Mar  9 2010 Josh Kayse <joshkayse@fedoraproject.org> - 3.2-1
- update to 3.2

* Sun Mar 07 2010 Josh Kayse <joshkayse@fedoraproject.org> - 3.1-2
- removed conflicts as it violates fedora packaging policy

* Sun Mar 07 2010 Josh Kayse <joshkayse@fedoraproject.org> - 3.1-1
- update to 3.1
- add explicit enable-shared
- add conflicts mod_python < 3.3.1

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul 02 2009 James Bowes <jbowes@redhat.com> 2.5-1
- Update to 2.5

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Nov 30 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 2.3-2
- Rebuild for Python 2.6

* Tue Oct 28 2008 Luke Macken <lmacken@redhat.com> 2.3-1
- Update to 2.3

* Mon Sep 29 2008 James Bowes <jbowes@redhat.com> 2.1-2
- Remove requires on httpd-devel

* Wed Jul 02 2008 James Bowes <jbowes@redhat.com> 2.1-1
- Update to 2.1

* Mon Jun 16 2008 Ricky Zhou <ricky@fedoraproject.org> 1.3-4
- Build against the shared python lib.

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.3-3
- Autorebuild for GCC 4.3

* Sun Jan 06 2008 James Bowes <jbowes@redhat.com> 1.3-2
- Require httpd

* Sat Jan 05 2008 James Bowes <jbowes@redhat.com> 1.3-1
- Update to 1.3

* Sun Sep 30 2007 James Bowes <jbowes@redhat.com> 1.0-1
- Initial packaging for Fedora

