%define debug_package %{nil}

Name:		prometheus
Version:	2.17.1
Release:	1%{?dist}
Packager:	Sergei Lavrov <ccppprogrammer@gmail.com>
Summary:	Prometheus an open-source monitoring system.
License:	GPLv3
Group:		Monitoring
URL:		https://github.com/prometheus/prometheus/
Source0:	https://github.com/prometheus/prometheus/releases/download/v%{version}/prometheus-%{version}.linux-amd64.tar.gz
Source1:	prometheus.systemd.service
Source2:	prometheus.yml

%if 0%{?fedora} > 16 || 0%{?rhel} > 6
Requires(pre): shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%else
Requires(post): chkconfig
Requires(preun):chkconfig
Requires(preun):initscripts
%endif

%description
An open-source monitoring system with a dimensional data model, flexible query language, efficient time series database and modern alerting approach.

%prep
%setup -q -n %{name}-%{version} -c

%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
useradd -r -g %{name} -d %{_sharedstatedir}/%{name} -s /sbin/nologin \
-c "prometheus" %{name} 2>/dev/null || :

%post
%if 0%{?fedora} > 16 || 0%{?rhel} > 6
if [ $1 -eq 1 ] ; then
	# Initial installation
	/bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi
%else
/sbin/chkconfig --add %{name}
%endif
/bin/chown -R %{name}:%{name} %{_sharedstatedir}/%{name}

%preun
%if 0%{?fedora} > 16 || 0%{?rhel} > 6
if [ $1 -eq 0 ] ; then
	/bin/systemctl --no-reload disable %{name}.service > /dev/null 2>&1 || :
	/bin/systemctl stop %{name}.service > /dev/null 2>&1 || :
fi
%else
if [ $1 = 0 ]; then
	/sbin/service %{name} stop > /dev/null 2>&1
	/sbin/chkconfig --del %{name}
fi
%endif

%build

%install
rm -rf $RPM_BUILD_ROOT
for i in rules rules.d files_sd consoles console_libraries; do mkdir -p $RPM_BUILD_ROOT/etc/%{name}/${i}; done
mkdir -p $RPM_BUILD_ROOT%{_libdir}/%{name}
install -D -m 0755 -p prometheus-%{version}.linux-amd64/prometheus $RPM_BUILD_ROOT%{_bindir}/prometheus
install -D -m 0755 -p prometheus-%{version}.linux-amd64/promtool $RPM_BUILD_ROOT%{_bindir}/promtool
install -D -m 0755 -p prometheus-%{version}.linux-amd64/consoles/* $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/consoles/
install -D -m 0755 -p prometheus-%{version}.linux-amd64/console_libraries/* $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/console_libraries/
install -D -m 0644 -p %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/%{name}.yml
%if 0%{?fedora} > 16 || 0%{?rhel} > 6
	install -D -m 0644 -p %{SOURCE1} $RPM_BUILD_ROOT%{_unitdir}/%{name}.service
%endif

%files
%defattr(-,%{name},%{name},-)
%{_bindir}/*
%{_sysconfdir}/%{name}/*
%dir %{_libdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.yml
%if 0%{?fedora} > 16 || 0%{?rhel} > 6
	%{_unitdir}/%{name}.service
%endif

%clean
rm -rf $RPM_BUILD_DIR/%{name}-%{version}
rm -rf $RPM_BUILD_ROOT

%changelog
* Mon Apr 20 2020 Sergei Lavrov <ccppprogrammer@gmail.com> - 2.17.1-1
- Add prometheus-2.17.1
