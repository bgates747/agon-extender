#include "adapter.hpp"
namespace agon::extender::webdav {
namespace {
using Headers = std::map<std::string, std::string>;
const char *allow =
    "OPTIONS, PROPFIND, GET, HEAD, PUT, MKCOL, MOVE, COPY, DELETE";
void reply(Output &out, int status, const std::string &body = "",
           Headers h = {}) {
  h["Connection"] = "close";
  h["Cache-Control"] = "no-store";
  if (!body.empty() && !h.count("Content-Type"))
    h["Content-Type"] = "text/plain; charset=utf-8";
  if (!out.begin(status, h, body.size()) ||
      (!body.empty() && !out.write(body.data(), body.size())))
    out.abort();
}
// Strict bounded XML subset for PROPFIND. Namespace resolution for DAV property
// names, no DTD/entities/CDATA or nonempty property values. Unknown namespaces
// are retained for truthful 404 propstats rather than silently treated as DAV.
struct Property {
  std::string ns, name;
};
struct Props {
  bool all = true, names = false;
  std::vector<Property> selected;
};
class Properties {
  std::string_view text;
  size_t at = 0;
  Props &out;
  using NS = std::map<std::string, std::string>;
  struct Tag {
    std::string name, ns, raw;
    NS scope;
    bool empty = false;
  };
  void ws() {
    while (at < text.size() && std::strchr(" \t\r\n", text[at]))
      ++at;
  }
  std::string token() {
    size_t a = at;
    while (at < text.size() && ((text[at] >= 'a' && text[at] <= 'z') ||
                                (text[at] >= 'A' && text[at] <= 'Z') ||
                                (text[at] >= '0' && text[at] <= '9') ||
                                std::strchr("_:.-", text[at])))
      ++at;
    return std::string(text.substr(a, at - a));
  }
  bool open(Tag &t, const NS &parent) {
    ws();
    if (at >= text.size() || text[at++] != '<')
      return false;
    t.raw = token();
    if (t.raw.empty())
      return false;
    t.scope = parent;
    for (;;) {
      ws();
      if (at >= text.size())
        return false;
      if (text[at] == '>') {
        ++at;
        break;
      }
      if (text[at] == '/' && at + 1 < text.size() && text[at + 1] == '>') {
        at += 2;
        t.empty = true;
        break;
      }
      auto a = token();
      if (a != "xmlns" && a.rfind("xmlns:", 0) != 0)
        return false;
      ws();
      if (at >= text.size() || text[at++] != '=')
        return false;
      ws();
      if (at >= text.size())
        return false;
      char q = text[at++];
      if (q != '\'' && q != '"')
        return false;
      auto b = at;
      while (at < text.size() && text[at] != q)
        ++at;
      if (at == text.size() || at - b > 120)
        return false;
      std::string v(text.substr(b, at - b));
      ++at;
      if (v.find_first_of("&<>") != v.npos)
        return false;
      t.scope[a == "xmlns" ? "" : a.substr(6)] = v;
    }
    auto colon = t.raw.find(':');
    std::string prefix = colon == t.raw.npos ? "" : t.raw.substr(0, colon);
    t.name = colon == t.raw.npos ? t.raw : t.raw.substr(colon + 1);
    auto startsName = [](const std::string &s) {
      return !s.empty() && ((s[0] >= 'a' && s[0] <= 'z') ||
                            (s[0] >= 'A' && s[0] <= 'Z') || s[0] == '_');
    };
    if (!startsName(t.name) || (!prefix.empty() && !startsName(prefix)) ||
        t.name.find(':') != t.name.npos)
      return false;
    auto it = t.scope.find(prefix);
    if (!prefix.empty() && it == t.scope.end())
      return false;
    t.ns = it == t.scope.end() ? "" : it->second;
    return true;
  }
  bool close(const Tag &t) {
    if (t.empty)
      return true;
    ws();
    std::string end = "</" + t.raw + ">";
    if (text.substr(at, end.size()) != end)
      return false;
    at += end.size();
    return true;
  }

public:
  Properties(std::string_view s, Props &p) : text(s), out(p) {}
  bool parse() {
    for (unsigned char c : text)
      if (c < 32 && c != 9 && c != 10 && c != 13)
        return false;
    ws();
    if (at == text.size())
      return true;
    if (text.substr(at, 5) == "<?xml") {
      auto end = text.find("?>", at + 5);
      if (end == text.npos)
        return false;
      at = end + 2;
    }
    Tag root;
    if (!open(root, {}) || root.ns != "DAV:" || root.name != "propfind" ||
        root.empty)
      return false;
    Tag mode;
    if (!open(mode, root.scope) || mode.ns != "DAV:")
      return false;
    if (mode.name == "allprop" || mode.name == "propname") {
      out.names = mode.name == "propname";
      if (!close(mode))
        return false;
    } else if (mode.name == "prop") {
      out.all = false;
      if (!mode.empty) {
        for (;;) {
          ws();
          if (text.substr(at, 2) == "</")
            break;
          Tag prop;
          if (out.selected.size() >= 24 || !open(prop, mode.scope) ||
              !close(prop))
            return false;
          out.selected.push_back({prop.ns, prop.name});
        }
        if (!close(mode))
          return false;
      }
    } else
      return false;
    if (!close(root))
      return false;
    ws();
    return at == text.size();
  }
};
std::string element(const Property &p, const Entry &e, bool names,
                    bool &known) {
  known = p.ns == "DAV:" &&
          (p.name == "displayname" || p.name == "resourcetype" ||
           p.name == "getcontentlength" || p.name == "getcontenttype" ||
           p.name == "supportedlock" || p.name == "lockdiscovery");
  if (e.directory &&
      (p.name == "getcontentlength" || p.name == "getcontenttype"))
    known = false;
  std::string tag = "X:" + p.name, attrs = " xmlns:X=\"" + xml(p.ns) + "\"";
  if (names || !known || p.name == "supportedlock" || p.name == "lockdiscovery")
    return "<" + tag + attrs + "/>";
  std::string value;
  if (p.name == "displayname")
    value = xml(e.path == "/" ? "/" : e.path.substr(e.path.rfind('/') + 1));
  if (p.name == "resourcetype" && e.directory)
    value = "<D:collection/>";
  if (p.name == "getcontentlength")
    value = std::to_string(e.size);
  if (p.name == "getcontenttype")
    value = "application/octet-stream";
  return "<" + tag + attrs + ">" + value + "</" + tag + ">";
}
std::string entryXml(const Entry &e, const Props &p) {
  std::vector<Property> fields = p.selected;
  if (p.all) {
    for (auto name :
         {"displayname", "resourcetype", "supportedlock", "lockdiscovery"})
      fields.push_back({"DAV:", name});
    if (!e.directory) {
      fields.push_back({"DAV:", "getcontentlength"});
      fields.push_back({"DAV:", "getcontenttype"});
    }
  }
  std::string good, bad;
  for (auto &f : fields) {
    bool known;
    auto s = element(f, e, p.names, known);
    (known ? good : bad) += s;
  }
  std::string out = "<D:response><D:href>" + encode(e.path) +
                    (e.directory && e.path != "/" ? "/" : "") + "</D:href>";
  if (!good.empty() || bad.empty())
    out += "<D:propstat><D:prop>" + good +
           "</D:prop><D:status>HTTP/1.1 200 OK</D:status></D:propstat>";
  if (!bad.empty())
    out += "<D:propstat><D:prop>" + bad +
           "</D:prop><D:status>HTTP/1.1 404 Not Found</D:status></D:propstat>";
  return out + "</D:response>";
}
bool validEntry(const Entry &e) {
  std::string checked;
  return path(encode(e.path), checked) && checked == e.path;
}
} // namespace
void Adapter::handle(const Request &q, Input &input, Output &out) {
  size_t headerSize = 0;
  for (auto &h : q.headers) {
    headerSize += h.first.size() + h.second.size();
    if (h.first != folded(h.first) ||
        h.second.find_first_of("\r\n") != h.second.npos) {
      reply(out, 400);
      return;
    }
  }
  if (q.headers.size() > 32 || headerSize > 4096 || q.uri.size() > 360) {
    reply(out, 413);
    return;
  }
  std::string source;
  if (!path(q.uri, source)) {
    reply(out, 400);
    return;
  }
  const auto &m = q.method;
  if (m == "OPTIONS") {
    reply(out, 200, "", {{"Allow", allow}});
    return;
  } // no DAV class claim yet
  if (m != "PROPFIND" && m != "GET" && m != "HEAD" && m != "PUT" &&
      m != "MKCOL" && m != "MOVE" && m != "COPY" && m != "DELETE") {
    reply(out, 405, "", {{"Allow", allow}});
    return;
  }
  // No pretend evaluation of lock tokens, entity tags or timestamp conditions.
  for (auto key :
       {"if", "if-range", "if-unmodified-since", "if-modified-since"})
    if (q.headers.count(key)) {
      reply(out, 501);
      return;
    }
  for (auto key : {"if-match", "if-none-match"})
    if (q.headers.count(key) && q.header(key) != "*") {
      reply(out, 501);
      return;
    }
  if (q.headers.count("content-encoding") || q.headers.count("content-range")) {
    reply(out, 415);
    return;
  }
  bool chunked = false;
  std::uint32_t length = 0;
  if (q.headers.count("transfer-encoding")) {
    if (q.header("transfer-encoding") != "chunked" ||
        q.headers.count("content-length") || m != "PUT" ||
        !number(q.header("x-expected-entity-length"), length)) {
      reply(out, 400);
      return;
    }
    chunked = true;
  } else if (q.headers.count("content-length")) {
    if (!number(q.header("content-length"), length)) {
      reply(out, 400);
      return;
    }
  } else if (m == "PUT") {
    reply(out, 411);
    return;
  }
  if (m != "PUT" && m != "PROPFIND" && length) {
    reply(out, m == "MKCOL" ? 415 : 400);
    return;
  }
  if (m == "PROPFIND" && length > 4096) {
    reply(out, 413);
    return;
  }
  std::string depth = q.header("depth");
  if (m == "PROPFIND" && (depth != "0" && depth != "1")) {
    reply(out, 403,
          "<D:error xmlns:D=\"DAV:\"><D:propfind-finite-depth/></D:error>",
          {{"Content-Type", "application/xml"}});
    return;
  }
  if ((m == "MOVE" || m == "DELETE") && !depth.empty() && depth != "infinity") {
    reply(out, 400);
    return;
  }
  if (m == "COPY" && !depth.empty() && depth != "0" && depth != "infinity") {
    reply(out, 400);
    return;
  }
  Operation op{m, source, "", false, depth != "0"};
  if (m == "MOVE" || m == "COPY") {
    std::string dest = q.header("destination");
    if (dest.rfind("http://", 0) == 0 || dest.rfind("https://", 0) == 0) {
      auto slash = dest.find('/', dest.find("://") + 3);
      if (slash == dest.npos || dest.substr(0, slash) != origin_) {
        reply(out, 502);
        return;
      }
      dest.erase(0, slash);
    }
    if (!path(dest, op.destination) || overlap(source, op.destination)) {
      reply(out, 403);
      return;
    }
    auto o = q.header("overwrite");
    if (!o.empty() && o != "T" && o != "F") {
      reply(out, 400);
      return;
    }
    op.overwrite = o != "F";
  }
  if (m == "PUT")
    op.overwrite = q.header("if-none-match") != "*";
  if (busy_.test_and_set()) {
    reply(out, 503, "Another request owns the mainboard service.");
    return;
  }
  struct Busy {
    std::atomic_flag &b;
    ~Busy() { b.clear(); }
  } busy{busy_};
  int status = backend_.begin(op);
  if (status != 200) {
    reply(out, status);
    return;
  }
  struct Lease {
    Backend &b;
    bool closed = false;
    ~Lease() {
      if (!closed)
        b.cancel();
    }
    int finish() {
      int s = b.finish();
      closed = true;
      return s;
    }
  } lease{backend_};
  Entry existing;
  status = backend_.stat(source, existing);
  bool exists = status == 200;
  if (status != 200 && status != 404) {
    reply(out, status);
    return;
  }
  if ((q.header("if-match") == "*" && !exists) ||
      (q.header("if-none-match") == "*" && exists)) {
    reply(out, (exists && q.header("if-none-match") == "*" &&
                (m == "GET" || m == "HEAD"))
                   ? 304
                   : 412);
    return;
  }
  if (!exists && m != "PUT" && m != "MKCOL") {
    reply(out, 404);
    return;
  }
  if (exists && (!validEntry(existing) || existing.path != source)) {
    reply(out, 500);
    return;
  }
  Body body(input, length, chunked);
  if (m == "PROPFIND") {
    std::string requestBody;
    std::array<char, 256> buf{};
    int got;
    while ((got = body.read(buf.data(), buf.size())) > 0)
      requestBody.append(buf.data(), got);
    Props props;
    if (got < 0 || !Properties(requestBody, props).parse()) {
      reply(out, 400);
      return;
    }
    // Bound listing metadata before emitting 207; a listing failure cannot be
    // concealed inside an already-successful response. No recursive listing.
    std::vector<Entry> entries{existing};
    bool full = false, invalid = false;
    if (existing.directory && depth == "1")
      status = backend_.list(source, [&](const Entry &e) {
        auto parent = e.path.substr(0, e.path.rfind('/'));
        if (parent.empty())
          parent = "/";
        if (!validEntry(e) || parent != source || e.path == source) {
          invalid = true;
          return false;
        }
        if (entries.size() >= 513) {
          full = true;
          return false;
        }
        entries.push_back(e);
        return true;
      });
    if (full || invalid || status != 200) {
      reply(out, full ? 507 : invalid ? 500 : status);
      return;
    }
    if ((status = lease.finish()) != 200) {
      reply(out, status);
      return;
    }
    if (!out.begin(207,
                   {{"Content-Type", "application/xml; charset=utf-8"},
                    {"Connection", "close"},
                    {"Cache-Control", "no-store"}},
                   -1)) {
      out.abort();
      return;
    }
    std::string start = "<?xml version=\"1.0\" "
                        "encoding=\"utf-8\"?><D:multistatus xmlns:D=\"DAV:\">";
    if (!out.write(start.data(), start.size())) {
      out.abort();
      return;
    }
    for (auto &e : entries) {
      auto x = entryXml(e, props);
      if (!out.write(x.data(), x.size())) {
        out.abort();
        return;
      }
    }
    const char *end = "</D:multistatus>";
    if (!out.write(end, std::strlen(end)))
      out.abort();
    return;
  }
  if (m == "GET" || m == "HEAD") {
    if (existing.directory) {
      reply(out, 405);
      return;
    }
    Range selected;
    status =
        range(m == "HEAD" ? "" : q.header("range"), existing.size, selected);
    if (status != 200 && status != 206) {
      reply(out, status, "",
            {{"Content-Range", "bytes */" + std::to_string(existing.size)}});
      return;
    }
    struct Snapshot {
      Backend &b;
      bool active = false;
      ~Snapshot() {
        if (active)
          b.releaseSnapshot();
      }
    } snap{backend_};
    if (m == "GET") {
      std::uint32_t size = 0;
      snap.active = true;
      auto s = backend_.snapshot(source, size);
      if (s != 200 || size != existing.size) {
        reply(out, s == 200 ? 409 : s);
        return;
      }
    }
    if (int s = lease.finish(); s != 200) {
      reply(out, s);
      return;
    }
    Headers h{{"Content-Type", "application/octet-stream"},
              {"Accept-Ranges", "bytes"},
              {"Connection", "close"},
              {"Cache-Control", "no-store"}};
    if (selected.partial)
      h["Content-Range"] = "bytes " + std::to_string(selected.start) + "-" +
                           std::to_string(selected.start + selected.count - 1) +
                           "/" + std::to_string(existing.size);
    if (!out.begin(status, h, selected.count)) {
      out.abort();
      return;
    }
    if (m == "HEAD")
      return;
    std::array<std::uint8_t, 4096> buffer{};
    while (selected.count) {
      size_t want = std::min<size_t>(selected.count, buffer.size()), n = 0;
      if (backend_.readSnapshot(selected.start, buffer.data(), want, n) !=
              200 ||
          !n || n > want || !out.write(buffer.data(), n)) {
        out.abort();
        return;
      }
      selected.start += n;
      selected.count -= n;
    }
    return;
  }
  Outcome result;
  if (m == "PUT") {
    if (exists && existing.directory) {
      reply(out, 409);
      return;
    }
    result = backend_.put(source, length, op.overwrite, body);
    if (result.status == 200 && !body.finished())
      result.status = 500;
  } else if (m == "MKCOL") {
    if (exists) {
      reply(out, 405);
      return;
    }
    result = backend_.mkdir(source);
  } else if (m == "DELETE")
    result = backend_.remove(source);
  else {
    Entry target;
    int s = backend_.stat(op.destination, target);
    if (s != 200 && s != 404) {
      reply(out, s);
      return;
    }
    if (s == 200 && !op.overwrite) {
      reply(out, 412);
      return;
    }
    exists = s == 200;
    // Current MOVE primitive cannot replace, and tree COPY cannot merge. Refuse
    // before changing anything, never emulate overwrite via destructive delete.
    if (exists && (m == "MOVE" || target.directory || existing.directory)) {
      reply(out, 501);
      return;
    }
    result = m == "MOVE" ? backend_.move(source, op.destination, false)
                         : backend_.copy(source, op.destination, op.overwrite,
                                         op.recursive);
  }
  if (result.status != 200) {
    if (result.completed) {
      std::string failure =
          result.failedPath.empty() ? source : result.failedPath;
      std::string xmlBody =
          "<D:multistatus xmlns:D=\"DAV:\"><D:response><D:href>" +
          encode(failure) + "</D:href><D:status>HTTP/1.1 " +
          std::to_string(result.status) + " " + reason(result.status) +
          "</D:status></D:response><D:responsedescription>Stopped after " +
          std::to_string(result.completed) +
          " completed entries; remaining work not "
          "executed.</D:responsedescription></D:multistatus>";
      reply(out, 207, xmlBody, {{"Content-Type", "application/xml"}});
    } else
      reply(out, result.status);
    return;
  }
  if ((status = lease.finish()) != 200) {
    reply(out, status);
    return;
  }
  reply(out, m == "DELETE" ? 204 : exists ? 204 : 201);
}
} // namespace agon::extender::webdav
