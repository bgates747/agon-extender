#include "selection.hpp"
#include <cassert>
#include <vector>
using namespace scroll_fixture;
int main() {
    for(int id=0;id<8;++id) {
        assert(select(names[id])==id);
        std::vector<unsigned> calls;
        assert(dispatch(id,[&](unsigned n){calls.push_back(n);return true;}));
        assert(calls==std::vector<unsigned>{unsigned(id)});
    }
    std::vector<unsigned> calls;
    assert(select("all")==8);
    assert(dispatch(8,[&](unsigned n){calls.push_back(n);return true;}));
    assert((calls==std::vector<unsigned>{0,1,2,3,4,5,6,7}));
    calls.clear();
    assert(!dispatch(8,[&](unsigned n){calls.push_back(n);return n!=2;}));
    assert((calls==std::vector<unsigned>{0,1,2}));
    assert(select("bogus")==-1);
    assert(!dispatch(-1,[](unsigned){assert(false);return true;}));
    assert(valid_label("retry-2_A"));
    assert(!valid_label("../bad")&&!valid_label("")&&!valid_label("has space"));
    assert(!valid_label("1234567890123456789012345"));
}
