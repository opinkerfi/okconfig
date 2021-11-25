%{!?python_version: %define python_version %(%{__python} -c "from distutils.sysconfig import get_python_version; print get_python_version()")}
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define is_suse %(test -e /etc/SuSE-release && echo 1 || echo 0)
%define release 1

Summary: Python Nagios Template management and configuration power tools
Name: okconfig
Version: 1.4.2
Release: %{release}%{?dist}
Source0: https://github.com/opinkerfi/okconfig/archive/%{name}-%{version}-%{release}.tar.gz
License: GPLv2
Group: System Environment/Libraries
Requires: python >= 2.3
BuildRequires: python-devel
%if %is_suse
BuildRequires: gettext-devel
%else
%if 0%{?fedora} >= 16
BuildRequires: python-setuptools
%else
%if 0%{?fedora} >= 8
BuildRequires: python-setuptools-devel
%else
%if 0%{?rhel} >= 5
BuildRequires: python-setuptools
%endif
%endif
%endif
%endif

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Url: http://github.com/opinkerfi/okconfig
BuildArch: noarch
Requires: pynag python-paramiko winexe
Requires: nagios-plugins-nrpe  nagios-plugins-ping nagios-plugins-ssh
Requires: nagios-okplugin-apc nagios-okplugin-brocade nagios-okplugin-mailblacklist
Requires: nagios-okplugin-check_disks nagios-okplugin-check_time nagios-plugins-fping

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
mkdir -m 775 -p $RPM_BUILD_ROOT/etc/nagios/okconfig
mkdir -m 775 -p $RPM_BUILD_ROOT/etc/nagios/okconfig/groups
mkdir -m 775 -p $RPM_BUILD_ROOT/etc/nagios/okconfig/hosts
mkdir -m 775 -p $RPM_BUILD_ROOT/etc/nagios/okconfig/templates
mkdir -m 775 -p $RPM_BUILD_ROOT/etc/nagios/okconfig/examples
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
%doc AUTHORS README.md LICENSE CHANGES
%{_datadir}/%{name}
%config(noreplace) %{_sysconfdir}/profile.d/nagios.csh
%config(noreplace) %{_sysconfdir}/profile.d/nagios.sh
%config(noreplace) %{_sysconfdir}/okconfig.conf
%config(noreplace) %{_sysconfdir}/bash_completion.d/okconfig
%config(noreplace) %{_sysconfdir}/logrotate.d/okconfig
#%{_mandir}/man1/okconfig.1.gz
%defattr(0775, nagios, nagios)
%attr(0770, nagios, nagios) %dir %{_localstatedir}/log/okconfig
%dir %{_sysconfdir}/nagios/okconfig
%dir %{_sysconfdir}/nagios/okconfig/groups
%dir %{_sysconfdir}/nagios/okconfig/hosts
%dir %{_sysconfdir}/nagios/okconfig/templates
%dir %{_sysconfdir}/nagios/okconfig/examples

%post
# If upgrading, then run okconfig upgrade
if [ $1 == 2 ]; then
	okconfig upgrade
else
	okconfig init
	okconfig addgroup default
fi


%changelog
* Fri Oct 15 2021 Gardar Thorsteinsson <gardar@ok.is> 1.3.9-1
- pip build process upgraded

* Fri Oct 15 2021 Gardar Thorsteinsson <gardar@ok.is> 1.3.7-1
- pip build process upgraded

* Fri Oct 15 2021 Gardar Thorsteinsson <gardar@ok.is> 1.3.5-1
- Template upgrades

* Fri Apr 04 2018 Gardar Thorsteinsson <gardar@ok.is> 1.3.3-1
- Updated dependency list - removed nagios-okplugin-apc nagios-okplugin-brocade nagios-okplugin-mailblacklist
- Template upgrades

* Wed Dec 06 2017 Gardar Thorsteinsson <gardar@ok.is> 1.3.2-1
- Template upgrades

* Fri Nov 17 2016 Gardar Thorsteinsson <gardar@ok.is> 1.3.1-1
- Updated dependency list - removed nagios package
- Added new service exclusions to windows template

* Tue Apr 30 2013 Pall Sigurdsson <palli@opensource.is> 1.1.1-1
- Version bump

* Tue Apr 30 2013 Pall Sigurdsson <palli@opensource.is> 1.1.0-1
- New release

* Tue Apr 30 2013 Pall Sigurdsson <palli@opensource.is>
- Version bump

* Tue Apr 30 2013 Pall Sigurdsson <palli@opensource.is> 1.0.11-1
- CHANGES updated (palli@opensource.is)
- http template, support for port and virtual_host macros (palli@opensource.is)
- Fix missing ipa check command (tommi@tommi.org)
- Added default ldaps connection to HOSTNAME (tommi@tommi.org)
- Added IPA support to okconfig (tommi@tommi.org)
- Merge branch 'master' of github.com:opinkerfi/okconfig (tommi@tommi.org)
- Added support for os-release and fedora 16-18 (tommi@tommi.org)
- support for comma seperated list of templates in addtemplate
  (palli@opensource.is)
- Fix warning about git global not being declared (palli@opensource.is)
- git commit on changes support (palli@opensource.is)
- Merge branch 'master' of github.com:opinkerfi/okconfig (palli@opensource.is)
- new configuration option: git_commit_changes (palli@opensource.is)
- Fix #28 okconfig.cfg->add examples_directory_local (gerdradecke@gmx.de)
- Missing quote for pipe in check_procs.sh (tommi@tommi.org)
- Missing quoting of backticks for check_procs.sh (tommi@tommi.org)
- Removed strong quoting for check_procs.sh (tommi@tommi.org)
- Closes 27 - Strong quoting cpu and proc checks (tommi@tommi.org)
- Added support for checking suspended RHCS services (tommi@tommi.org)
- Fix missing auth parameters in EMC check portstate (palli@lsh.is)

* Fri Oct 26 2012 Pall Sigurdsson <palli@opensource.is> 1.0.10-1
- Merge branch 'master' of github.com:opinkerfi/okconfig (palli@opensource.is)
- removed nsclient directory (palli@opensource.is)

* Fri Oct 26 2012 Pall Sigurdsson <palli@opensource.is> 1.0.9-1
- SNMP Connectivity removed from proliant example. Closes #5
  (palli@opensource.is)
- okconfig group default is now always created on install (Closes #9)
  (palli@opensource.is)
- --alias now supported with host templates (palli@opensource.is)
- windows update logo added (palli@opensource.is)
- Error handling improved on okconfig commands (palli@opensource.is)
- Apache example bugfixes (palli@opensource.is)
- add 'okconfig upgrade' to %%post section of rpm spec (palli@opensource.is)
- subcommands listtemplates and listhosts added (palli@opensource.is)
- addcontact: contact name can now be specified as argument from command-line
  (palli@opensource.is)
- addcontact contact_groups changed to contactgroups (palli@opensource.is)
- storwize templates added (palli@opensource.is)
- notes logo change (palli@opensource.is)
- wmi test added (palli@opensource.is)
- Brocade templates reworked (palli@opensource.is)
- icon updates (palli@opensource.is)
- passive host template updated (palli@opensource.is)
- APC templates reworked. Templates for all equipment supported by
  check_apcext.pl (palli@opensource.is)
- mge logo added (palli@opensource.is)
- windows logo added (palli@opensource.is)
- aix logo updated (palli@opensource.is)
- fix command_line for okc-check_https_certificate for rhel6 compatibility
  (palli@opensource.is)
- Added missing _SNMP_COMMUNITY macro (palli@opensource.is)
- Added monitoring templates for ACRC cooling units from apc
  (palli@opensource.is)
- fixed typo in brocade example (palli@opensource.is)
- check_cpu script now included in script (palli@opensource.is)
- experimental suse support for install_agent (palli@opensource.is)
- subprocess typo fixed (palli@opensource.is)
- except ValueError changed to except KeyError (palli@opensource.is)
- help_function.runCommand now uses stdin=subprocess.PIPE (palli@opensource.is)
- Fix okconfig install breaking on failures (palli@opensource.is)
- Various bugfixes (palli@opensource.is)
- host example now uses new okc-check_ping (palli@opensource.is)
- okc-check_ping added (palli@opensource.is)
- traceroute function added. (palli@opensource.is)
- subprocess module added to imports (palli@opensource.is)
- Added preliminary http support (tommi@tommi.org)
- path updated for check_gearman (palli@opensource.is)
- Gearman tests added to nagios template (palli@opensource.is)
- Merge branch 'master' of github.com:opinkerfi/okconfig (palli@opensource.is)
- fedora16 support deprecated for fedora17 (palli@opensource.is)

* Fri Aug 17 2012 Pall Sigurdsson <palli@opensource.is> 1.0.8-1
- MMCSS added to default excluded services (palli@opensource.is)
- "okconfig upgrade" now also detects deprecated host and service notification
  commands (Closes #8) (palli@opensource.is)
- fixed need for dns lookup to find default ip address (palli@opensource.is)
- invalid check_commands fixed in emc templates (palli@opensource.is)
- fixed typo in smbclient parameters (palli@opensource.is)
- Merge branch 'master' of github.com:opinkerfi/okconfig (palli@opensource.is)
- check_nrpe check command renamed to okc-check_nrpe (palli@opensource.is)
- Object definition rewritten (tommi@darkstar)
- Object definition rewritten (tommi@darkstar)
- Added register 0 to dell openmanage templates (tommi@tommi.org)
- bugfix, fixed mixing of sets and list in get_template (palli@opensource.is)
- Nagios config up-to-date added to nagios example (palli@opensource.is)
- fixed unhandled exception when examples_directory_local does not exist
  (palli@opensource.is)
- Templates for Dell Openmanage monitoring added (palli@opensource.is)
- Bugfix, get_templates() now returns templates that only exist in the local
  templates directory (root@mgmt.clarahq.com)
- bugfix where rhel6 distro was skipped (root@mgmt.clarahq.com)
- debian support for install_okagent.sh (palli@opensource.is)
- cleanup of print statements (palli@opensource.is)
- Merge branch 'master' of https://opensource.ok.is/git/okconfig
  (palli@opensource.is)
- template cleanup (palli@opensource.is)
- HOSTNAME, multi-inheritance removed (palli@opensource.is)
- Added missing register 0 for oracle and apache (tommi@tommi.org)
- runCommand() moved to helper_functions module (palli@opensource.is)
- .idea added to .gitignore (palli@opensource.is)
- releasers.conf updated to include source tarballs (palli@opensource.is)
- Merge branch 'master' of https://opensource.ok.is/git/okconfig
  (palli@opensource.is)
- releasers.conf updated and is now split into production and testing
  (palli@opensource.is)
- host-passive template renamed to .cfg-example (palli@opensource.is)

* Thu Jul 12 2012 Pall Sigurdsson <palli@opensource.is> 1.0.7-1
- Getting rid of multi-inheritance in examples (palli@opensource.is)
- unspecified group in addtemplate now uses the same group as host
  (palli@opensource.is)

* Wed Jul 11 2012 Pall Sigurdsson <palli@opensource.is> 1.0.6-1
- support for local .examples files implemented (palli@opensource.is)
- improvements to remote installation for windows (palli@opensource.is)
- dependencies for .spec file updated. Winexe fixes (palli@opensource.is)
- install_okagent.sh placed for linux agent installation (palli@opensource.is)
- install_nrpe and install_nsclient implemented (palli@opensource.is)
- Default thresholds for linux check_proc increased to warning=500
  critical=1000 (palli@opensource.is)
- init subcommand feature added (palli@opensource.is)
- bugfix in removehost when removing multiple hosts (palli@opensource.is)
- okconfig- deprecated and removed (palli@opensource.is)
- okc- prefix added to all commands. migrate script included
  (palli@opensource.is)
- removehost functionality added (palli@opensource.is)
-  etc/nagios/okconfig/templates directory added to rpm (palli@opensource.is)

* Thu May 31 2012 Tomas Edwardsson <tommi@tommi.org> 1.0.5-7
- Fixed permissions in spec file for /etc/nagios/okconfig (tommi@tommi.org)
- bash_completion updated to reflect new syntax (palli@opensource.is)
- groups now autogenerated if specified by addhost (palli@opensource.is)
- error handling added (palli@opensource.is)
- help and --help options added (palli@opensource.is)
- command line arguments redesigned (again) (palli@opensource.is)
* Wed May 30 2012 Tomas Edwardsson <tommi@tommi.org> 1.0.5-1
- Fixed rsync path for tito, was missing root user (tommi@tommi.org)
- Added F17 to tito build (tommi@tommi.org)
- new okconfig binary with new syntax (palli@opensource.is)
- Merge branch 'master' of https://opensource.ok.is/git/okconfig
  (palli@opensource.is)
- addservice function added (palli@opensource.is)
- host_template now configurable when adding new hosts (palli@opensource.is)
- Issue #55, removed mssql till requirements are satisfied (tommi@tommi.org)
- rhcs6 examples added (palli@opensource.is)

* Mon Mar 12 2012 Pall Sigurdsson <palli@opensource.is> 1.0.4-1
- / added to end of every reponame. okconfig.spec now support fedora 16
  (palli@opensource.is)
- added more repos to releasers.conf (palli@opensource.is)

* Mon Mar 12 2012 Pall Sigurdsson <palli@opensource.is> 1.0.3-1
- tito releasers.conf added (palli@opensource.is)
- manpages commented out (palli@opensource.is)

* Mon Mar 12 2012 Pall Sigurdsson <palli@opensource.is> 1.0.2-1
-

* Mon Mar 12 2012 Pall Sigurdsson <palli@opensource.is> 1.0.1-1
- new package built with tito

* Sun Oct  1 2011 Tomas Edwardsson <tommi@opensource.is> - 1.0-9
- Fixes to packaging and missing specifications

* Fri Jul 22 2011 Pall Sigurdsson <palli@opensource.is> - 1.0-1
- Initial RPM Creation, based heavily on the func spec file
