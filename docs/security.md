# Sylva Security

## X509 Certificate Management

### Internal PKI

Sylva management cluster is shipped with its own Root authority, implemented by a cert-manager `ClusterIssuer` (see below), for which the certificate can be retrieved as follows:

```shell
 kubectl -n cert-manager get secret ca-key-pair -o jsonpath='{.data.ca\.crt}' | base64 -d
```

It is recommended to import this CA certificate in your browser in order to verify the server certificates sent by the exposed applications like `rancher` and `keycloak`. The way to import a CA certificate depends on the OS and the browser and, thus, are not detailed in this document.

Then, the X509 certificate for your additional services in the management cluster can be issued from `cert-manager` by using the `ClusterIssuer` named `ca-issuer`, as illustrated below:

```yaml
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: rancher-tls
  namespace: cattle-system
spec:
  secretName: rancher-tls
  # Currently the certificate is trusted by the Sylva CA by referring to the ca-issuer.
  # It is possible to leverage an external authority by referring a vault-issuer or an acme-issuer.
  # In this case, configure the issuer according to the spec of the external authority and update issuerRef below
  issuerRef:
    name: ca-issuer
    kind: ClusterIssuer
  commonName: ${RANCHER_DNS}
  duration: 2160h # 90d
  renewBefore: 360h # 15d
  emailAddresses:
  - surname.name@sylva.org
  subject:
    organizations:
    - Sylva
    countries:
    - eu
    organizationalUnits:
    - DEV
  dnsNames:
  - ${RANCHER_DNS}
  - localhost
  ipAddresses:
  - 127.0.0.1
```

> **_Note_**: Enabling the PKI engine in Vault might allow the workload clusters requesting certifificate to be trusted by this root authority, typically by relying on a cert-manager Vault issuer. This feature is not yet supported but be likely included in one of the next releases.

### External PKI

Rather than using the internal PKI to sign the certificates of the exposed services, it is possible to import certificates signed by a trusted PKI. It improves the level of confidence in the received server certificates and avoids importing CA certificates in the browser (assuming that the CA certificate of the trusted CA is already part of the system bundle).

The steps to follow are:  

1. Create pairs of private key and certificate for every exposed service

   The way to obtain certificates depends on the authority delivering them, on the organisation of the project, ...  
   The script `./tools/generate_csr.sh` automates the generation of a key and of a CSR for each exposed service and can serve as an example. It expects one argument which is the domain of the platform being deployed. Environment values can be used to configure the subject of the certificates. Run `./tools/generate_csr.sh --help` for additional details. The CSRs can then be sent to the PKI which provides a certificate in return.

2. Add to `secrets.yaml` the dictionary `external_certificates`, with a `cacert` attribute to store external CA certificates (there can be several of them), and for each exposed service a `cert` and `key` attribute that can be set with the corresponding values.

   ```
   external_certificates:
     cacert: |
       -----BEGIN CERTIFICATE-----
       MIIGPTCCBCWgAwIBAgIBAjANBgkqhkiG9w0BAQsFADBdMQswCQYDVQQGEwJGUjEP
       MA0GA1UECgwGT3JhbmdlMRgwFgYDVQQLDA9GUiA4OSAzODAxMjk4NjYxIzAhBgNV
       BAMMGk9yYW5nZSBJbnRlcm5hbCBHMiBSb290IENBMB4XDTE2MDUwMzEzMjA0NFoX
       DTM2MDUwMzEzMjA0NFowXzELMAkGA1UEBhMCRlIxDzANBgNVBAoMBk9yYW5nZTEY
       MBYGA1UECwwPRlIgODkgMzgwMTI5ODY2MSUwIwYDVQQDDBxPcmFuZ2UgSW50ZXJu
   ...
       rnrCMsDkBfI/ZN+ITBcWi6cAyOcsIOk4up9aUvNJTMKUlEybDNN8cDp9+vLonN2h
       YMg1IfJ+IZs6x3rDr5MXuWTks34hEJidpmOTmOyy/QPHCK0BGRmUoYJr4CHS4FL2
       BtsnCPyUUO4gppjywfYrotQ2gTQ=
       -----END CERTIFICATE-----
     rancher:
       cert: |
         -----BEGIN CERTIFICATE-----
         MIIHGjCCBQKgAwIBAgIUQZbwTFCAIrOTzYhoONlRWCnUlcMwDQYJKoZIhvcNAQEL
         BQAwXzELMAkGA1UEBhMCRlIxDzANBgNVBAoMBk9yYW5nZTEYMBYGA1UECwwPRlIg
         ODkgMzgwMTI5ODY2MSUwIwYDVQQDDBxPcmFuZ2UgSW50ZXJuYWwgRzIgU2VydmVy
         IENBMB4XDTI0MDExNzA5MDgxN1oXDTI2MDExNzA5MDgxN1owgY0xNTAzBgNVBAMM
   ...
         TDOSuKCXFr9WUStNQNcqvezcyyuAMC58SqxP8uW/BtlkY9h4/9KXc45a8A1NtEYE
         BnrES9kJPCiCST87a8txsf0Gs9EweVY5ksoU+Dc3vDT2sYe5WqkgnwZg+lXRcBsB
         JBHNq501JPZOh+/bguj7VXLc396s+nGqRXw5rkduGchq+Vadrqp0H/uaa/v3jA==
         -----END CERTIFICATE-----
       key: |
         -----BEGIN PRIVATE KEY-----
         MIIJQQIBADANBgkqhkiG9w0BAQEFAASCCSswggknAgEAAoICAQCw6jGQ0rmsmd2s
         9inIMOVzbMrcNrWZeZNf6h4b83URqi9u16AzZuDHYjBLfOEzbpj/mHbSUrgVbO70
         JHxajLuF0RLEIolciGPIkPDdOqDAENy9fzXRqEQNwhXE/D9jFG5Ty2TU8Geiua+D
   ...
         mwoC8Kr8cHvKTd1F0cS63OUjkuLnZLlrUsudaXr9AidPDMpLjyyT9adUxICChTN8
         a3acBFjeI4kUczcbaM7vhcbveaE+4M2yjHRNMdgcCkVKL0BoBWitUAMeWXfP1lbh
         NZ4r8lYxJ5+srb0cUG3rERxqF+Bo
         -----END PRIVATE KEY-----
     keycloak:
       cert: |
         -----BEGIN CERTIFICATE-----
         MIIHHTCCBQWgAwIBAgIUZug0UtvZduX80eGW86GdlCYLfkowDQYJKoZIhvcNAQEL
         BQAwXzELMAkGA1UEBhMCRlIxDzANBgNVBAoMBk9yYW5nZTEYMBYGA1UECwwPRlIg
         ODkgMzgwMTI5ODY2MSUwIwYDVQQDDBxPcmFuZ2UgSW50ZXJuYWwgRzIgU2VydmVy
   ...
     flux:
   ...
     vault:
   ...
     neuvector:
     harbor:
   ...
     gitea:
   ...
   ```

3. Deploy or update the management cluster

Note 1: The services not defined in the `external_certificate` dictionary will be delivered a certificate signed by the internal PKI described in the previous section. So although it is not mandatory to provide an external certificate for all the exposed services (currently `rancher`, `keycloak`, `flux`, `vault`, `neuvector`, `harbor` and `gitea` at the time of this writing), it is advised to provide a certificate signed by the external PKI for all the services as soon as we do it for one.

Note 2: X509 certificate automation can leverage an external authority by updating the issuerRef in the manifest of the TLS certificates, for example by referring a vault-issuer or an acme-issuer, as stated [here](https://gitlab.com/sylva-projects/sylva-core/-/blame/main/kustomize-units/tls-components/tls-certificate/certificate.yaml?ref_type=heads#L13). However, this modifification is not supported in `sylva-core` Helm chart release 1.0 and must be done manually so far.

## Password Management

The Sylva units offering a web UI (`keycloak`, `rancher`, `vault`, `flux-webui`, `harbor` and `neuvector`) are configured with local administration accounts, whose passwords/tokens are unique and randomly generated.

The passwords for `Keycloak`, `Rancher`, `Neuvector`  and `flux-webui` can be retrieved from `Vault` (see next section).

In addition, Sylva is shipped with a Single-Sign-On (SSO) service provided by `Keycloak`. The user can thus connect to `Vault`, `Rancher`, `Flux-Webui` and `Neuvector` after being redirected once to `Keycloak` authentication. The SSO account to use is `sylva-admin` (login `sylva-admin`) from the  `Keycloak` realm `sylva`. The password for this account can be provided in your environment-values file `secrets.yaml` like showed below, but this not encouraged, except possibly for dev, test or CI environments.

```yaml
admin_password:  < a password following the password policy >
```

> **_IMPORTANT NOTICE:_** this password must follow the `Keycloak` password policy: length(12) and upperCase(1) and lowerCase(1) and digits(1), otherwise the user `sylva-admin` is not created.

The following command will generate a password compliant with the password policy:

```shell
< /dev/urandom tr -dc 'A-Za-z0-9' | head -c12
```

If you don't set a password here, helm shall pick a random one. You can retrieve it in `vault` (secret/sso-account) by using the vault root token to authenticate against Vault (see next section) or by using the following command:

```shell
 kubectl get secrets sylva-units-values -o template="{{ .data.values }}" | base64 -d | grep admin_password
```

## Vault

The passwords for `Keycloak`, `Rancher`, `flux-webui` and `Neuvector` can be retrieved from `Vault`. You can authenticate against `Vault` through the OIDC authentication method or by using the `Vault` root token. <br/>

> **_NOTE:_** If you don't provide `.admin_password` in the environment file `secrets.yaml`, connect to Vault by using the `Vault` root token and retrieve the randomly generated password for the SSO account in the vault path `/secret/sso-account`.

Note also that the OIDC authentication has restricted rights on `Vault` paths in comparison to the root token authentication, which, by nature, has full privileges on `Vault` resources:

| Privilege                                                                        | OIDC authentication | Root Token Authentication |
| -------------------------------------------------------------------------------- | ------------------- | ------------------------- |
| Read Secret                                                                      | yes                 | yes                       |
| Update and Create Secret                                                         | no                  | yes                       |
| Manage secrets engines                                                           | no                  | yes                       |
| Create, update, and delete auth methods                                          | yes                 | yes                       |
| Create and manage system policies                                                | yes                 | yes                       |
| Read system health check                                                         | yes                 | yes                       |
| Manage system backend other than health auth and policy (audit, config, etc... ) | no                  | yes                       |

### OIDC authentication

![vault-login-oidc](./img/security/vault-oidc.png)

![vault-oidc-redirection](./img/security/vault-oidc-redirect.png)

Once authenticated against `Vault`, the local account password of each management cluster service can be retrieved either from the `Vault GUI` or the `Vault CLI`.

### Token authentication

You can retrieve the Vault token with the following command.

```shell
kubectl -n vault get secret vault-unseal-keys -o jsonpath='{.data.vault-root}' | base64 -d
```

![vault-login-token](./img/security/vault-token.png)

### Retrieve Secrets from Vault GUI

![vault-secrets](./img/security/vault-paths.png)

### Retrieve Secrets from Vault CLI

```shell
export VAULT_TOKEN=$(kubectl -n vault get secret vault-unseal-keys -o jsonpath='{.data.vault-root}' | base64 -d)
kubectl -n vault get secret vault-tls -o jsonpath='{.data.ca\.crt}' | base64 -d > vault-ca.crt
export VAULT_ADDR=https://vault.sylva
export VAULT_CACERT=$PWD/vault-ca.crt
```

```shell
$ vault kv list secret
Keys
----
flux-webui
keycloak
rancher
sso-account
```

```shell
$ vault kv get secret/rancher
=== Secret Path ===
secret/data/rancher

======= Metadata =======
Key                Value
---                -----
created_time       2023-06-09T13:49:58.903341566Z
custom_metadata    <nil>
deletion_time      n/a
destroyed          false
version            1

============ Data ============
Key                      Value
---                      -----
bootstrapPassword        <..bla bla..>
```

## Identity and Access Management

Identity and Access Management is addressed by `Keycloak` providing user management, single-sign-on, user federation and identity brokering.

### Keycloak Admin Console

To administrate `Keycloak`, go to the "Keycloak GUI", e.g. `https://keycloak.sylva` and select the [Administration Console](https://keycloak.sylva/admin/master/console).

![keycloak-ui](./img/security/keycloak-ui.png)

Then use the password in `Vault` under the path `secret/keycloak` to authenticate against `Keycloak` (the login name is `admin` by default, see sections above to learn how to get secrets from `Vault`).

> **_NOTE_**: when connecting to the administration console, you are logged in as administrator of the realm `master`. The administrator gets all privileges on other realms, i.e. `sylva`. It is thus useless to connect to the realm `sylva` with the `sylva-admin` credentials. Actually if this credential might grant access to realm `sylva`, it has no authorizations on `Keycloak` resources.

![keycloak-login](./img/security/keycloak-login.png)

### Password Policy

Any passwords generated by Sylva follows a password policy enforced either on `Keycloak` (for user creation) or `Vault` (for generation of random secrets). For example, below is the policy definition at `Vault` side:

```yaml
apiVersion: redhatcop.redhat.io/v1alpha1
kind: PasswordPolicy
metadata:
  name: sylva-password-policy
spec:
  <snip>
  # password policy specified using Vault password policy syntax (https://www.vaultproject.io/docs/concepts/password-policies#password-policy-syntax)
  passwordPolicy: |
    length = 12
    rule "charset" {
    charset = "abcdefghijklmnopqrstuvwxyz"
    min-chars = 1
    }
    rule "charset" {
    charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    min-chars = 1
    }
    rule "charset" {
    charset = "0123456789"
    min-chars = 1
    }

```

### User Management

The users and groups are centralized on `Keycloak`. They can be created on `Keycloak` (as depicted below) or imported from an external user federation (LDAP, AD, etc...)

> **_IMPORTANT NOTICE:_** Configuring an external user federation is out of scope of Sylva. However, if an external user federation is configured, the local `keycloak` accounts (e.g. `sylva-admin`) cannot be used anymore, unless the federation is configured to allow `keycloak` writing in the remote user directory. However granting such a privilege to `Keycloak` might raise a security risk that should be seriously evaluated.

![keycloak-users](./img/security/keycloak-user.png)

![keycloak-groups](./img/security/keycloak-groups.png)

![keycloak-group-members](./img/security/keycloak-group-members.png)

#### External Identity Provider

It can be interesting to configure Keycloak to rely on an external identity provider, for example `Gitlab.com` as shown below, or even your own company's IDP.

```json
{
  realm                   = "sylva"
  client_id               = "4ac6........885"
  client_secret           = "a9f.........b19"
  alias                   = "oidc"
  authorization_url       = "https://gitlab.com/oauth/authorize"
  user_info_url           = "https://gitlab.com/oauth/userinfo"
  token_url               = "https://gitlab.com/oauth/token"
  default_scopes          = "openid email profile"
  display_name            = "Gitlab"

  extra_config = {
    "clientAuthMethod" = "client_secret_post"
  }
}
```

![keycloak-idps](./img/security/keycloak-idp.png)

### Access Control to workload Clusters

If `Keycloak` plays a key role in access control to the workload cluster, it must be clear that `Keycloak` only manages the authentication of the users. The authorization part (i.e. define who can do what) is configured at the OIDC client (i.e. `Rancher`) side. For example, the following picture shows Rancher binding the admin role to the group infra-admins:

![Rancher-role-binding](./img/security/role-binding.png)

You can manage the binding from the Rancher Web UI via the `sylva-admin` account but, note that in this case, the  `sylva-admin`  account must be member of the Keycloak groups to bind. It is clearly unwanted and, thus, the group binding via the `Rancher` web-ui is only for testing purpose.

It is recommended to not use the GUI but to manage the group binding the via Rancher CRD (`globalrolebinding`, `projectroletemplatebindings` and `clusterroletemplatebindings`) or even with [Terraform Rancher provider](https://registry.terraform.io/providers/rancher/rancher2/latest/docs). Below are examples of CRD based binding:

```yaml
apiVersion: management.cattle.io/v3
kind: GlobalRoleBinding
metadata:
  name: grb-infra-admins
  annotations:
    cleanup.cattle.io/grbUpgradeCluster: "true"
    lifecycle.cattle.io/create.mgmt-auth-grb-controller: "true"
  finalizers:
  - controller.cattle.io/mgmt-auth-grb-controller
globalRoleName: admin
groupPrincipalName: keycloakoidc_group://infra-admins
```

Summarizing, `Rancher` acts as an authentication proxy, allowing a fine-grained access control relying on `Keycloak` users/groups management as depicted below.

![sylva-rbac](./img/security/sylva-rbac.jpg)

> **_IMPORTANT SECURITY NOTICE:_** the Rancher administrator has access to the resources of the the workload clusters, in particular to the volumes and to the k8s secrets of the workload clusters. As a consequence **it is crucial to have a strict access control on who is allowed to connect as an administrator to Rancher**.

## Kubernetes Security

High Security Grade clusters SHOULD rely on RKE2. RKE2 is hardened by default and pass the majority of the Kubernetes CIS controls without modification. RKE2 claims to focus on security and compliance within the U.S. Federal Government sector by:

- Providing defaults and configuration options that allow clusters to pass the CIS Kubernetes Benchmark v1.6 with minimal operator intervention.
- Enabling FIPS 140-2 compliance.
- Regularly scanning components for CVEs in Rancher build pipeline.

For a complete list of security controls, please refer to https://docs.rke2.io/security/cis_self_assessment16/.

When high security grade is required, Sylva can deploy RKE2 clusters with a `cis_profile` set to `cis-1.6` or `cis-1.23` depending on the Kubernetes release. The profile validates the system configuration against the corresponding CIS benchmark. This flag makes RKE2 check that host-level requirements have been met. It also configures runtime pod security policies and network policies (please refer to https://docs.rke2.io/security/hardening_guide/ for additional details).

### RKE2 Security Scan

Sylva includes the Kubernetes operator [cis-operator](https://github.com/rancher/cis-operator) that provides the ability to run  RKE2  security scans against the the CIS benchmark:

```shell
$ kubectl get clusterscans
NAME                CLUSTERSCANPROFILE              TOTAL   PASS   FAIL   SKIP   WARN   NOT APPLICABLE   LASTRUNTIMESTAMP   
rke2-cis-hardened   rke2-cis-1.6-profile-hardened   122     82     4      0      29     7                2023-04-28T14:45:22Z   
```

#### Fetch Scan Reports with kubectl

Scan summaries are obtained with the command `kubectl get clusterscans -o yaml`. You can also get more detailed scan reports with few `kubectl` commands:

```shell
$ kubectl get clusterscanreports
NAME                                  LASTRUNTIMESTAMP                                            BENCHMARKVERSION
scan-report-rke2-cis-hardened-drnh8   2022-10-28 14:45:40.019124438 +0000 UTC m=+2336.836186254   rke2-cis-1.6-hardened   
```

The report is in JSON format:

```shell
$ kubectl get clusterscanreport scan-report-rke2-cis-hardened-drnh8 -o jsonpath="{.spec.reportJSON}" | jq
{
  "version": "rke2-cis-1.6-hardened",
  "total": 122,
  "pass": 82,
  "fail": 4,
  "skip": 0,
  "warn": 29,
  "notApplicable": 7,
....
```

You can parse this JSON file and issue an human readable report with the Python script `display-scan-report.py` available [here](../tools/display-scan-report.py), which can be used as follows:

```shell
$ kubectl get $(kubectl get clusterscanreports -o name) \
-o jsonpath="{.spec.reportJSON}" \
| ./display-scan-report.py
```

#### Getting Scan Reports from Rancher

![ClusterScanReport](./img/security/cis-report.png)

![cis-result](./img/security/cis-result.png)

### Kubeadm Security Scan

You can issue security scan on `kubeadm` cluster by enabling the unit `trivy-operator` in in your environment file `values.yaml`:

```yaml
units:
  trivy-operator:
    enabled: yes
```

The `trivy-operator`  includes the CRD  `clustercompliancereports`, which provide can reports against various benchmark:

```shell
$ kubectl get clustercompliancereports
NAME             AGE
cis              4h4m
nsa              4h4m
pss-baseline     4h4m
pss-restricted   4h4m
```

Choosing the CIS benchmark:

```shell
kubectl get clustercompliancereports cis -o yaml
```

### Vulnerabilities Check

#### Trivy-Operator

To check vulnerabilities of **running** images, enable the deployment of trivy-operator in your `environment-values` file `values.yaml`:

```yaml
units:
  trivy-operator:
    enabled: yes
```

You can list the vulnerabilities reports and get a summary with the command:

```shell
kubectl get -A vulnerabilityreports -o wide
```

Then we can focus on a report and dig into it for details:

```shell
$ kubectl get -n calico-system vulnerabilityreport replicaset-calico-typha-89798ff7b-calico-typha -o wide
NAME                                             REPOSITORY                      TAG       SCANNER   AGE   CRITICAL   HIGH
replicaset-calico-typha-89798ff7b-calico-typha   rancher/mirrored-calico-typha   v3.25.0   Trivy     12m   1          1  
```

```shell
kubectl get -n calico-system vulnerabilityreport replicaset-calico-typha-89798ff7b-calico-typha -o yaml
```

It should issue a report like this:

```yaml
report:
  artifact:
    repository: rancher/mirrored-calico-typha
    tag: v3.25.0
  registry:
    server: index.docker.io
  scanner:
    name: Trivy
    vendor: Aqua Security
    version: 0.40.0
  summary:
    criticalCount: 1
    highCount: 1
    lowCount: 0
    mediumCount: 0
    noneCount: 0
    unknownCount: 0
  updateTimestamp: "2023-07-13T12:30:06Z"
  vulnerabilities:
  - fixedVersion: 2.16.0+incompatible
    installedVersion: v2.11.2-0.20200112161605-a7c079c43d51+incompatible
    links: []
    primaryLink: https://avd.aquasec.com/nvd/cve-2022-1996
    resource: github.com/emicklei/go-restful
    score: 9.1
    severity: CRITICAL
    target: ""
    title: Authorization Bypass Through User-Controlled Key
    vulnerabilityID: CVE-2022-1996
  - fixedVersion: 0.7.0
    installedVersion: v0.4.0
    links: []
    primaryLink: https://avd.aquasec.com/nvd/cve-2022-41723
    resource: golang.org/x/net
    score: 7.5
    severity: HIGH
    target: ""
    title: avoid quadratic complexity in HPACK decoding
    vulnerabilityID: CVE-2022-41723
```

> **_Note_** that trivy-operator includes, in addition to the vulnerability assessment, a bunch of audit and compliancy reports that are worth to be considered:

```shell
$ kubectl api-resources | grep aqua
clustercompliancereports                     compliance                         aquasecurity.github.io/v1alpha1            false        ClusterComplianceReport
clusterconfigauditreports                    clusterconfigaudit                 aquasecurity.github.io/v1alpha1            false        ClusterConfigAuditReport
clusterinfraassessmentreports                clusterinfraassessment             aquasecurity.github.io/v1alpha1            false        ClusterInfraAssessmentReport
clusterrbacassessmentreports                 clusterrbacassessmentreport        aquasecurity.github.io/v1alpha1            false        ClusterRbacAssessmentReport
configauditreports                           configaudit,configaudits           aquasecurity.github.io/v1alpha1            true         ConfigAuditReport
exposedsecretreports                         exposedsecret,exposedsecrets       aquasecurity.github.io/v1alpha1            true         ExposedSecretReport
infraassessmentreports                       infraassessment,infraassessments   aquasecurity.github.io/v1alpha1            true         InfraAssessmentReport
rbacassessmentreports                        rbacassessment,rbacassessments     aquasecurity.github.io/v1alpha1            true         RbacAssessmentReport
vulnerabilityreports                         vuln,vulns                         aquasecurity.github.io/v1alpha1            true         VulnerabilityReport

```

## Software Bill Of Material (SBOM)

The optional unit `sbom-operator` allows to build the Software Bill Of Material (SBOM) of Sylva. The unit deploys an [operator](https://artifacthub.io/packages/helm/ckotzbauer/sbom-operator) generating the SBOM of each image used in a Sylva cluster.

By default, the SBOMs is exported to `confimaps`, which can be retrieved as follows:

```shell
kubectl  get -A configmap -l ckotzbauer.sbom-operator.io
```

The `configmap` content is stored as `broli` compressed binary-data. The following commands show how to fetch a given SBOM:

```shell
kubectl  get -n kyverno configmap kyverno-cleanup-admission-reports-28146180-l6jv2-cleanup -o jsonpath='{.binaryData.sbom}' | base64 -d > sbom.br

brotli -d sbom.br
```

Instead of `configmaps`, the SBOMs can be exported to Git, OCI registry or [Dependency Track](https://owasp.org/www-project-dependency-track/). The later is an interesting OWASP tool for the analysis of the SBOM's component. To build  and export the Sylva SBOMs to an external Dependency Track server, you can modify the `values.yaml` of the `sbom-operator` chart file as follows:

```yaml
serviceAccount:
  create: true
  name: sbom-operator
securityContext:
   capabilities:
     drop:
     - ALL
   privileged: false
   readOnlyRootFilesystem: true
   runAsNonRoot: true
   runAsUser: 10001
   seccompProfile:
     type: RuntimeDefault
resources:
   limits:
     cpu: 500m
     memory: 500Mi
   requests:
     cpu: 100m
     memory: 100Mi
args:
  targets: dtrack
  verbosity: debug
  format: cyclonedx
  dtrack-base-url: https://dependency-track.example
  dtrack-api-key: xGNE...
envVars: # if using proxy
      - name: https_proxy
        value: http://proxy.example:8080
      - name: http_proxy
        value: http://proxy.example:8080
      - name: no_proxy
        value: localhost,127.0.0.0/8,192.168.0.0/16,172.16.0.0/12,10.0.0.0/8,172.20.36.130,keycloak.sylva,.cluster.local,.cluster.local.,.svc
```

Dependency track displays all imported SBOMs and gives a summary of the vulnerabilities for each of them:

![dt-projects](./img/security/dt-projects.png)

Then, for each images, we can have the list of components (softwares and packages) and check for their vulnerabilities:

![dt-components](./img/security/dt-component-vulns.png)

## Suse Neuvector

The optional unit "Neuvector" addresses the platform Zero Trust Security by providing vulnerability Management, Compliance, Runtime Security, Supply Chain Security, Network Visibility and Container Segmentation. Please refer to the [SUSE Neuvector Official documentation](https://www.suse.com/products/neuvector/) for further details.

### Neuvector admin console

To administrate Neuvector, you can access its Web UI: `https://neuvector.<cluster_domain_name>`,  e.g. at https://neuvector.sylva.

![neuvecto-login](./img/security/neuvector-login.png)

### OIDC authentication

To login with OIDC clic on the "Login with OpenID" button.

![neuvector-oidc-redirection](./img/security/neuvector-oidc-redirect.png)

Then enter a personal identifier and password.
The user must belong to the `infra-admins` group in Keycloak in order to be able to modify the configuration, or to the `neuvector-readers` group in order to have a read-only access.

### Local authentication

To login with a local account click on the "Login" button.
The only account provisioned is `admin`. You can retrieve the password from Vault under the path `secret/neuvector`.
Connection with this account should be reserved to emergency cases, when OIDC authentication is broken.

### Neuvector dashboard

![neuvector-dashboard](./img/security/neuvector-dashboard.png)

From the Neuvector dashboard you can:

- visualize the network activity
- manage the assets
- manage the policy
- manage the security risks
- manage the Notifications
- manage Neuvector settings

### Neuvector modes

Neuvector defines 3 modes for the resources scanned.

- Discover. In this mode Neuvector discovers the infrastructure, the running services and applications and automatically builds white list of network rules
- Monitor. In this mode Neuvector monitors run-time violations of security events and raises security events
- Protect. In this mode Neuvector blocks any network violation and attacks detected

Neuvector default settings keep resources in discover mode. Manual action is needed to switch them to Monitor mode.

It is recommended to rapidly switch to the monitor mode, then after a reasonable observation period, switch to the Protect mode. Note that the Protect mode can raise denial of services if resource control policies are poorly learned.

### Network activity

![neuvector-network-activity](./img/security/neuvector-network-activity.png)

The view can be filtered by criteria such as namespaces to make it more readable.
This view highlights unexpected network flows that correspond potentially to malicious behaviors.

### Assets management

From the assets management menu you can:

- visualize the platforms registered on Neuvector and launch security scans
- visualize the namespaces and their resources (workloads, pods, services)
- visualize the nodes and access to the result of their compliance check and their vulnerabilities
- visualize the containers and their state

### Policies management

From the Policy management menu you can:

- add, update or remove admission control policies
- add, update or remove group policies
- add, update or remove network policies

### security risks management

From the Policy management menu you can manage:

- Vulnerabilies and vulnerabilities profile
- Compliance and compliance profile

### notification management

From the Notification management menu you can display:

- security events, which include three sub-types: violation, threats, and incidents
- risk reports
- events

Note that Notification are stored in memory with a rolling limit of 4K per type and sub-type.

**It is recommended to forward these security events to a SIEM system** by configuring the Syslog feature under Settings > Configuration > Syslog.
