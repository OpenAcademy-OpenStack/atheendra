import keystoneclient.v2_0.client as ksclient
import glanceclient.v2.client as glclient
import novaclient.v1_1.client as nvclient
import credentials
import time

default_name = "ubuntu"
default_flavor = "m1.micro"

keystone_creds = credentials.get_keystone_creds()

#Get images containing Ubuntu
keystone = ksclient.Client(**keystone_creds)
glance_endpoint = keystone.service_catalog.url_for(
                                    service_type='image',
                                    endpoint_type='publicURL')
glance = glclient.Client(glance_endpoint, token=keystone.auth_token)
ubuntu_images = [ img for img in glance.images.list() 
                            if default_name in img["name"]]

#Create images
nova_creds = credentials.get_nova_creds()
nova = nvclient.Client(**nova_creds)
flavor = nova.flavors.find(name="m1.micro")
created_instances = [
        nova.servers.create(name=img["name"]+"_vm",
                            image=img["id"],
                            flavor=flavor)
        for img in ubuntu_images
        ]

#Check for instance creation success
for instance in created_instances:
    while nova.servers.get(instance.id).status == "BUILD":
        time.sleep(5)
    status = nova.servers.get(instance.id).status 
    if(status == "ERROR"):
        print "Error creating instance: " + instance.name
    else:
        print "Instance " + instance.name + " started successfully"
