%{!?python_version: %define python_version %(%{__python} -c "from distutils.sysconfig import get_python_version; print get_python_version()")}
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define is_suse %(test -e /etc/SuSE-release && echo 1 || echo 0)

Summary: Python Nagios Template management and configuration power tools
Name: okconfig
Version: 1.0
Release: 4%{?dist}
Source0: http://opensource.is/files/%{name}-%{version}.tar.gz
License: GPLv2
Group: System Environment/Libraries
Requires: python >= 2.3
BuildRequires: python-devel
%if %is_suse
BuildRequires: gettext-devel
%else
%if 0%{?fedora} >= 8
BuildRequires: python-setuptools-devel
%else
%if 0%{?rhel} >= 5
BuildRequires: python-setuptools
%endif
%endif
%endif
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Url: http://opensource.is/trac
BuildArch: noarch 

%description
A robust template mechanism for Nagios configuration files. Providing
standardized set of configuration templates and select quality plugins 
to enterprise quality monitoring.



%prep
%setup -q

%build
%{__python} setup.py build

%install
test "x$RPM_BUILD_ROOT" != "x" && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --prefix=/usr --root=$RPM_BUILD_ROOT
install -m 755 -d usr/share/okconfig $RPM_BUILD_ROOT/%{_datadir}/%{name}
mkdir -p $RPM_BUILD_ROOT/etc/bash_completion.d/
mkdir -p $RPM_BUILD_ROOT/etc/profile.d/
install -m 644 etc/okconfig.conf $RPM_BUILD_ROOT/%{_sysconfdir}/
install -m 644 etc/bash_completion.d/* $RPM_BUILD_ROOT/%{_sysconfdir}/bash_completion.d/
install -m 644 etc/profile.d/* $RPM_BUILD_ROOT/%{_sysconfdir}/profile.d/

%clean
rm -fr $RPM_BUILD_ROOT

%files
%defattr(-, root, root, -)
%if "%{python_version}" >= "2.5"
%{python_sitelib}/okconfig*.egg-info
%endif
%dir %{python_sitelib}/okconfig
%{python_sitelib}/okconfig/*.py*
%{_bindir}/okconfig
%doc AUTHORS README LICENSE CHANGES
%{_datadir}/%{name}
%config(noreplace) %{_sysconfdir}/profile.d/nagios.csh
%config(noreplace) %{_sysconfdir}/profile.d/nagios.sh
%config(noreplace) %{_sysconfdir}/okconfig.conf
%config(noreplace) %{_sysconfdir}/bash_completion.d/okconfig
%{_mandir}/man1/okconfig.1.gz


%changelog
* Sun Oct  1 2011 Tomas Edwardsson <tommi@opensource.is> - 1.0-4
- Initial RPM Creation, based heavily on the func spec file

* Fri Jul 22 2011 Pall Sigurdsson <palli@opensource.is> - 1.0-1
- Initial RPM Creation, based heavily on the func spec file
