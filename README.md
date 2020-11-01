# mg-helper

mg-helper is a python application which performs post-processing on a must-gather to make the data more accessible and friendly.  

# Reflecting POD/Service names instead of raw IP addresses in pod logs

When reading pod logs it is quite challenging to know what pod or service is associated with a given IP address.  As a result, you have to perform a set of searches to find the IP and the associated resource.

To transform the pod log files to replace the raw IP address with the name of the pod or service you must provide the path to the must-gather as well as enable the "Pod IP Mapping" plugin.

For example:
~~~
python3 ./xmg.py -a /run/media/rvanderp/ssd2/tmp/must-gather.local.5965513261844107622 -e "Pod IP mapping"
~~~

Depending on the number of pods in the must-gather, this can take a few minutes.  

You will end up with logs which are annotated with the service/pod names.  

For example:
~~~
2020-03-19T21:19:11.757569568-07:00 E0320 04:19:11.757521    4979 reflector.go:270] github.com/openshift/machine-config-operator/pkg/generated/informers/externalversions/factory.go:101: Failed to watch *v1.MachineConfig: Get https://[svc:kubernetes@172.30.0.1]443/apis/machineconfiguration.openshift.io/v1/machineconfigs?resourceVersion=39269845&timeout=5m14s&timeoutSeconds=314&watch=true: dial tcp [svc:kubernetes@172.30.0.1]443: connect: no route to host
2020-03-19T21:19:14.763544793-07:00 E0320 04:19:14.763494    4979 reflector.go:126] k8s.io/client-go/informers/factory.go:133: Failed to list *v1.Node: Get https://[svc:kubernetes@172.30.0.1]443/api/v1/nodes?limit=500&resourceVersion=0: dial tcp [svc:kubernetes@172.30.0.1]443: connect: no route to host
~~~
