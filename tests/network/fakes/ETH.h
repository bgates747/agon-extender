#pragma once
#include <string>
#include <cassert>
constexpr int ETH_PHY_IP101=101, EMAC_CLK_EXT_IN=1;
struct FakeAddress {std::string toString() const{return "test-address";}};
struct FakeEthernet {
 bool fail=false, up=false;
 unsigned starts=0,stops=0;
 bool begin(int phy,int address,int mdc,int mdio,int power,int clock) {
  assert(phy==ETH_PHY_IP101&&address==1&&mdc==31&&mdio==52&&power==51&&clock==EMAC_CLK_EXT_IN);
  ++starts;up=!fail;return up;
 }
 void end(){++stops;up=false;}
 bool hasIP() const{return up;}
 bool linkUp() const{return up;}
 FakeAddress localIP()const{return {};}
 FakeAddress subnetMask()const{return {};}
 FakeAddress gatewayIP()const{return {};}
 FakeAddress dnsIP()const{return {};}
};
inline FakeEthernet ETH;
