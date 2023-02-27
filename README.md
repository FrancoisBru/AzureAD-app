# API_MSAL
This Python script aims to assign administrators roles to users for an Azure Active Directory

To start using this tool you may need to :

1)Install podman if Docker fails to launch HTTPS requests : sudo apt install podman

2) If resolv.conf is not installed on your machine : sudo apt-get install --reinstall resolvconf
Then add : "nameserver your_dns_ip_address"
sudo service podman restart

3)sudo podman -t build choose_a_name .

4)Sudo podman run -i -t name_chosen_in_step_3 


