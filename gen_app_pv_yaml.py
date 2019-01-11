import os

APP_COUNT = 2
PVC_PER_APP = 10

PVC_HEADER1 = '---\n\
kind: PersistentVolumeClaim\n\
apiVersion: v1\n\
metadata:\n'

PVC_HEADER2 = '\
spec:\n\
  storageClassName: glusterblock-csi\n\
  accessModes:\n\
    - ReadWriteOnce\n\
  resources:\n\
    requests:\n\
      storage: 1Gi\n'

APP_HEADER1 = '---\n\
apiVersion: v1\n\
kind: Pod\n\
metadata:\n'

APP_HEADER2='\
  labels:\n\
    app: smallfile\n\
spec:\n\
  containers:\n\
  - name: smallfile\n\
    image: quay.io/ekuric/smallfile:latest\n\
    imagePullPolicy: IfNotPresent\n\
    volumeMounts:\n'

APP_HEADER3='\
  volumes:\n'

file = "/tmp/pvc-app1.yml"
with open(file, 'w') as f:
    pv_count = 1
    pvc_claim = 1
    for i in range(1, APP_COUNT):
        for j in range(1,PVC_PER_APP):
            f.write(PVC_HEADER1)
            f.write('  name: glusterblock-%d\n' % pv_count)
            f.write(PVC_HEADER2)
            pv_count += 1
        f.write(APP_HEADER1)
        f.write('  name: gluster-%d\n' % i)
        f.write(APP_HEADER2)
        for k in range(1,13):
            f.write('    - name: glustercsivol-%d\n' % k)
            f.write('      mountPath: "/mnt/gluster-%d"\n' % k)
        f.write(APP_HEADER3)
        for l in range(1,13): 
            f.write('  - name: glustercsivol-%d\n' % l)
            f.write('    persistentVolumeClaim:\n')
            f.write('      claimName: glusterblock-%d\n' % pvc_claim)
            pvc_claim += 1

print "Generated file: %s" % file
