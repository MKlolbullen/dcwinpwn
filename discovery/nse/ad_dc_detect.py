description = [[Detect likely Active Directory Domain Controllers via LDAP RootDSE/Kerberos]]
author = "linWinPwn-next"
license = "Same as Nmap--See https://nmap.org/book/man-legal.html"
categories = {"discovery"}

portrule = function(host, port)
  return port.protocol == "tcp" and (port.number == 389 or port.number == 636 or port.number == 88)
end

action = function(host, port)
  local out = "AD hint: DC detection via port " .. port.number
  return out
end
