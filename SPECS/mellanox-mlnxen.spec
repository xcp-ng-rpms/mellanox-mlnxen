%global package_speccommit be1cce316a8f1a042816a88caf5fe97adc385c3f
%global usver 5.9_0.5.5.0
%global xsver 2
%global xsrel %{xsver}%{?xscount}%{?xshash}
%global package_srccommit 5.9_0.5.5.0
%define vendor_name Mellanox
%define vendor_label mellanox
%define driver_name mlnxen

%if %undefined module_dir
%define module_dir updates
%endif

## kernel_version will be set during build because then kernel-devel
## package installs an RPM macro which sets it. This check keeps
## rpmlint happy.
%if %undefined kernel_version
%define kernel_version dummy
%endif

Summary: %{vendor_name} %{driver_name} device drivers
Name: %{vendor_label}-%{driver_name}
Version: 5.9_0.5.5.0
Release: %{?xsrel}%{?dist}
License: GPLv2
Source0: mellanox-mlnxen-5.9_0.5.5.0.tar.gz

BuildRequires: gcc
BuildRequires: kernel-devel >= 4.19.19-8.0.29
%{?_cov_buildrequires}
Provides: vendor-driver
Requires: kernel-uname-r = %{kernel_version}
Requires: kernel >= 4.19.19-8.0.29
Requires(post): /usr/sbin/depmod
Requires(postun): /usr/sbin/depmod

%description
%{vendor_name} %{driver_name} device drivers for the Linux Kernel
version %{kernel_version}.

%prep
%autosetup -p1 -n %{name}-%{version}
%{?_cov_prepare}

%build
export EXTRA_CFLAGS='-DVERSION=\"%version\"'
export KSRC=/lib/modules/%{kernel_version}/build
export KVERSION=%{kernel_version}

find compat -type f -exec touch -t 200012201010 '{}' \; || true
./scripts/mlnx_en_patch.sh --kernel $KVERSION --kernel-sources $KSRC %{?_smp_mflags}
%{?_cov_wrap} %{__make} V=0 %{?_smp_mflags}

%install
export INSTALL_MOD_PATH=%{buildroot}
export INSTALL_MOD_DIR=%{module_dir}
export KSRC=/lib/modules/%{kernel_version}/build
export KVERSION=%{kernel_version}

%{?_cov_wrap} %{__make} install KSRC=$KSRC MODULES_DIR=$INSTALL_MOD_DIR DESTDIR=%{buildroot} KERNELRELEASE=$KVERSION DEPMOD=/bin/true
# Cleanup unnecessary kernel-generated module dependency files.
find %{buildroot}/lib/modules -iname 'modules.*' -exec rm {} \;

# mark modules executable so that strip-to-file can strip them
find %{buildroot}/lib/modules/%{kernel_version} -name "*.ko" -exec mv '{}' %{buildroot}/lib/modules/%{kernel_version}/%{module_dir} \;
find %{buildroot}/lib/modules/%{kernel_version} -name "*.ko" -type f | xargs chmod u+x

%{?_cov_install}

%post
/sbin/depmod %{kernel_version}
%{regenerate_initrd_post}

%postun
/sbin/depmod %{kernel_version}
%{regenerate_initrd_postun}

%posttrans
%{regenerate_initrd_posttrans}

%files
/lib/modules/%{kernel_version}/*/*.ko

%{?_cov_results_package}

%changelog
* Mon Sep 25 2023 Stephen Cheng <stephen.cheng@citrix.com> - 5.9_0.5.5.0-2
- CP-45398: Update to version 5.9-0.5.5.0

* Mon Aug 07 2023 Stephen Cheng <stephen.cheng@citrix.com> - 5.4_1.0.3.0-4
- CP-41018: Use auxiliary.ko in kernel to resolve the conflict with intel-ice

* Thu Feb 24 2022 Ross Lagerwall <ross.lagerwall@citrix.com> - 5.4_1.0.3.0-3
- CP-38416: Enable static analysis

* Mon Oct 18 2021 Igor Druzhinin <igor.druzhinin@citrix.com> - 5.4_1.0.3.0-2
- CP-38292: Introduce MLNX_EN 5.4-1.0.3.0 driver
