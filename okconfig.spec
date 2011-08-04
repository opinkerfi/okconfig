%{!?python_version: %define python_version %(%{__python} -c "from distutils.sysconfig import get_python_version; print get_python_version()")}
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define is_suse %(test -e /etc/SuSE-release && echo 1 || echo 0)

Summary: Python Nagios Template management and config powertools
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

%description
OKConfig is a robust templating mechanism for Nagios configuration files. Providing standardized set of configuration templates and pre-selected quality plugins to enterprise quality monitoring.


%package examples
Group: System Environment/Libraries
Summary: Example scripts which manipulate Nagios configuration

%description examples
Example scripts which manipulate Nagios configuration files. Provided
are scripts which list services, do network discovery amongst others.


%prep
%setup -q

%build
%{__python} setup.py build

%install
test "x$RPM_BUILD_ROOT" != "x" && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --prefix=/usr --root=$RPM_BUILD_ROOT
#mkdir -p $RPM_BUILD_ROOT/usr/share/pynag
install -m 755 -d usr/share/okconfig $RPM_BUILD_ROOT/%{_datadir}/%{name}
mkdir -p $RPM_BUILD_ROOT/etc/bash_completion.d/
mkdir -p $RPM_BUILD_ROOT/etc/profile.d/
install -m 755 etc/okconfig.conf $RPM_BUILD_ROOT/%{_sysconfdir}/
install -m 755 etc/bash_completion.d/* $RPM_BUILD_ROOT/%{_sysconfdir}/bash_completion.d/
install -m 755 etc/profile.d/* $RPM_BUILD_ROOT/%{_sysconfdir}/profile.d/
#install -m 755  usr/share/okconfig/* $RPM_BUILD_ROOT/%{_datadir}/%{name}
#cp -rf usr/share/okconfig $RPM_BUILD_ROOT/%{_datadir}/%{name}

%clean
rm -fr $RPM_BUILD_ROOT

%files
%defattr(-, root, root, -)
%if "%{python_version}" >= "2.5"
%{python_sitelib}/pynag*.egg-info
%endif
%dir %{python_sitelib}/okconfig
%{python_sitelib}/okconfig/*.py*
%{_bindir}/okconfig
%doc AUTHORS README LICENSE CHANGES
#%{_mandir}/man1/pynag-add_host_to_group.1.gz
#%{_mandir}/man1/pynag-safe_restart.1.gz
%{_datadir}/%{name}
%{_sysconfdir}

%changelog
* Fri Jul 22 2011 Tomas Edwardsson <palli@opensource.is> - 1.0-1
- Initial RPM Creation, based heavily on the func spec file
