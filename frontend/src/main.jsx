import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { Check, CreditCard, Home, LogIn, LogOut, MapPin, Minus, PackageCheck, Plus, Search, ShoppingBag, ShoppingCart, Trash2, UserRound, X } from "lucide-react";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const currency = new Intl.NumberFormat("fa-IR");
const normalizeList = (payload) => (Array.isArray(payload) ? payload : payload?.results || []);
const apiUrl = (path) => `${API_BASE}${path}`;
const visualAssets = [
  "https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=1200&q=85",
  "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=1200&q=85",
  "https://images.unsplash.com/photo-1517433367423-c7e5b0f35086?auto=format&fit=crop&w=1200&q=85",
  "https://images.unsplash.com/photo-1509365465985-25d11c17e812?auto=format&fit=crop&w=1200&q=85",
  "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=1200&q=85",
  "https://images.unsplash.com/photo-1514517220037-1c02489e01a6?auto=format&fit=crop&w=1200&q=85",
];
const croissantImage = "https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=1200&q=90";
const fallbackImage = (seed = "") => visualAssets[Math.abs([...String(seed)].reduce((sum, ch) => sum + ch.charCodeAt(0), 0)) % visualAssets.length];
const mediaUrl = (value, seed) => (!value || value.endsWith("default.jpg") ? fallbackImage(seed) : value.startsWith("http") ? value : `${API_BASE}${value}`);

async function request(path, options = {}) {
  const token = localStorage.getItem("access_token");
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(apiUrl(path), { ...options, headers });
  const text = await response.text();
  const body = text ? JSON.parse(text) : null;
  if (!response.ok) {
    const flat = body && typeof body === "object" ? Object.values(body).flat?.()[0] : null;
    throw new Error(body?.detail || body?.message || body?.error || flat || "درخواست با خطا روبرو شد.");
  }
  return body;
}

function App() {
  const [view, setView] = useState("home");
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [cart, setCart] = useState(null);
  const [cartOpen, setCartOpen] = useState(false);
  const [filters, setFilters] = useState({ search: "", category: "all", ordering: "" });
  const [authOpen, setAuthOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(true);
  const [authTick, setAuthTick] = useState(0);
  const isAuthed = Boolean(localStorage.getItem("access_token"));
  const effectiveCategory = view === "category" && selectedCategory ? selectedCategory.category_id : filters.category;

  useEffect(() => { bootstrap(); }, [authTick]);
  useEffect(() => { loadProducts(); }, [effectiveCategory, filters.ordering]);

  const visibleProducts = useMemo(() => {
    const q = filters.search.trim().toLowerCase();
    return products.filter((item) => {
      if (q && !`${item.name} ${item.description || ""}`.toLowerCase().includes(q)) return false;
      return true;
    });
  }, [products, filters.search]);
  const heroProduct = visibleProducts[0] || products[0];
  const cartCount = cart?.items?.reduce((sum, item) => sum + item.quantity, 0) || 0;

  async function bootstrap() {
    setLoading(true);
    try { await Promise.all([loadProducts(), loadCategories(), isAuthed ? loadCart() : Promise.resolve(setCart(null))]); }
    finally { setLoading(false); }
  }
  async function loadProducts() {
    const params = new URLSearchParams();
    if (effectiveCategory !== "all") params.set("category_id", effectiveCategory);
    if (filters.ordering) params.set("ordering", filters.ordering);
    setProducts(normalizeList(await request(`/products/${params.toString() ? `?${params}` : ""}`)));
  }
  async function loadCategories() { setCategories(normalizeList(await request("/categories/"))); }
  async function loadCart() { const current = await request("/carts/current/"); setCart(current); return current; }
  function requireLogin() { setAuthOpen(true); setNotice("برای سبد خرید و سفارش ابتدا وارد حساب شوید."); }
  async function addToCart(product, quantity = 1) {
    if (!isAuthed) { requireLogin(); return; }
    try {
      const current = cart || await loadCart();
      await request(`/carts/${current.id}/items/`, { method: "POST", body: JSON.stringify({ product_id: product.id, quantity }) });
      await loadCart();
      setCartOpen(true);
      setNotice(`${product.name} به سبد خرید شما اضافه شد.`);
    } catch (error) { setNotice(error.message); }
  }
  async function updateItem(item, quantity) {
    try {
      if (quantity < 1) await request(`/carts/${cart.id}/items/${item.id}/`, { method: "DELETE" });
      else await request(`/carts/${cart.id}/items/${item.id}/`, { method: "PATCH", body: JSON.stringify({ quantity }) });
      await loadCart();
    } catch (error) { setNotice(error.message); }
  }
  function openCart() { if (!isAuthed) requireLogin(); else setCartOpen(true); }
  function openCheckout() {
    if (!isAuthed) { requireLogin(); return; }
    if (!cart?.items?.length) { setNotice("سبد خرید خالی است."); return; }
    setCartOpen(false); setView("checkout"); window.scrollTo({ top: 0, behavior: "smooth" });
  }
  function openCategory(category) {
    setSelectedCategory(category); setView("category"); window.scrollTo({ top: 0, behavior: "smooth" });
  }
  function logout() {
    localStorage.removeItem("access_token"); localStorage.removeItem("refresh_token");
    setCart(null); setView("home"); setAuthTick((v) => v + 1); setNotice("از حساب خارج شدید.");
  }

  return <main className="site-shell">
    <Header cartCount={cartCount} isAuthed={isAuthed} onAuth={() => setAuthOpen(true)} onCart={openCart} onProfile={() => isAuthed ? setProfileOpen(true) : requireLogin()} onLogout={logout} goHome={() => setView("home")} />
    {notice && <Toast message={notice} onClose={() => setNotice("")} />}
    {view === "checkout" ? <CheckoutPage cart={cart} loadCart={loadCart} setView={setView} setNotice={setNotice} /> : view === "category" ? <CategoryPage category={selectedCategory} products={visibleProducts} filters={filters} setFilters={setFilters} onAdd={addToCart} onBack={() => setView("home")} /> : <HomePage heroProduct={heroProduct} categories={categories} products={visibleProducts} filters={filters} setFilters={setFilters} loading={loading} onAdd={addToCart} onCategory={openCategory} />}
    {view !== "checkout" && <Footer onCart={openCart} onProfile={() => isAuthed ? setProfileOpen(true) : requireLogin()} />}
    {cartOpen && <CartDrawer cart={cart} onClose={() => setCartOpen(false)} onUpdate={updateItem} onCheckout={openCheckout} />}
    {authOpen && <AuthModal onClose={() => setAuthOpen(false)} onDone={() => { setAuthOpen(false); setAuthTick((v) => v + 1); }} setNotice={setNotice} />}
    {profileOpen && <ProfileModal onClose={() => setProfileOpen(false)} setNotice={setNotice} />}
  </main>;
}

function Footer({ onCart, onProfile }) { return <footer className="site-footer"><div><h2>Online Store Kian</h2><p>محصولات تازه، دسته‌بندی روشن، سبد خرید اختصاصی و تکمیل سفارش با آدرس انتخابی.</p></div><div className="footer-links"><a href="#menu">محصولات</a><button onClick={onCart}>سبد خرید</button><button onClick={onProfile}>پروفایل</button></div><div className="footer-meta"><span>Fresh bakery shop</span><span>Local checkout experience</span><span>2026</span></div></footer>; }

function Header({ cartCount, isAuthed, onAuth, onCart, onProfile, onLogout, goHome }) { return <header className="topbar solid"><button className="brand-mark" onClick={() => { goHome(); window.scrollTo({ top: 0, behavior: "smooth" }); }}>OSK</button><nav><a href="#menu">Menu</a><button onClick={onCart}>Cart</button><button onClick={onProfile}>Profile</button></nav><div className="header-actions"><button className="icon-button" onClick={onCart} title="سبد خرید"><ShoppingCart size={19} />{cartCount > 0 && <span>{cartCount}</span>}</button>{isAuthed ? <><button className="icon-button" onClick={onProfile} title="پروفایل"><UserRound size={19} /></button><button className="icon-button" onClick={onLogout} title="خروج"><LogOut size={19} /></button></> : <button className="login-button" onClick={onAuth}><LogIn size={18} /> ورود</button>}</div></header>; }
function HomePage({ heroProduct, categories, products, filters, setFilters, loading, onAdd, onCategory }) { return <><Hero product={heroProduct} onShop={() => document.getElementById("menu")?.scrollIntoView({ behavior: "smooth" })} onAdd={onAdd} /><section className="category-strip">{categories.map((cat) => <button key={cat.category_id} onClick={() => onCategory(cat)}>{cat.title}</button>)}</section><section id="menu" className="menu-section"><Toolbar filters={filters} setFilters={setFilters} categories={categories} total={products.length} />{loading ? <div className="product-grid">{Array.from({ length: 6 }).map((_, i) => <div className="skeleton-card" key={i} />)}</div> : <div className="product-grid">{products.map((product, index) => <ProductCard key={product.id} product={product} index={index} onAdd={onAdd} onOpen={() => onCategory(product.category)} />)}</div>}</section></>; }
function Hero({ product, onShop, onAdd }) { return <section className="hero black-hero"><div className="croissant-stage"><img className="hero-croissant real" src={croissantImage} alt="Croissant" /></div><div className="hero-content centered"><p className="eyebrow">Baked daily / سفارش آنلاین</p><h1 className="hero-title-slide">Online Store Kian</h1><p className="hero-copy">محصولات را از دسته‌بندی‌ها انتخاب کنید، سبد خرید را از کنار صفحه مدیریت کنید و سفارش را کامل پرداخت کنید.</p><div className="hero-actions"><button className="light-action" onClick={onShop}><ShoppingBag size={20} /> مشاهده محصولات</button>{product && <button className="ghost-action" onClick={() => onAdd(product)}><Plus size={20} /> افزودن پیشنهاد امروز</button>}</div></div></section>; }
function CategoryPage({ category, products, filters, setFilters, onAdd, onBack }) { return <section className="category-page"><div className="checkout-head"><button onClick={onBack}><Home size={18} /> همه محصولات</button><h1>{category?.title || "دسته‌بندی"}</h1></div><Toolbar filters={{ ...filters, category: category?.category_id || "all" }} setFilters={setFilters} categories={[]} total={products.length} hideCategory /> <div className="product-grid category-only">{products.map((product, index) => <ProductCard key={product.id} product={product} index={index} onAdd={onAdd} onOpen={() => {}} />)}</div></section>; }
function Toolbar({ filters, setFilters, categories, total, hideCategory = false }) { return <div className="toolbar"><div><p>Search</p><h2>انتخاب محصول</h2></div><div className="tools advanced"><label><Search size={18} /><input value={filters.search} onChange={(e) => setFilters({ ...filters, search: e.target.value })} placeholder="جستجوی نام یا توضیح" /></label>{!hideCategory && <select value={filters.category} onChange={(e) => setFilters({ ...filters, category: e.target.value })}><option value="all">همه دسته‌ها</option>{categories.map((cat) => <option key={cat.category_id} value={cat.category_id}>{cat.title}</option>)}</select>}<select value={filters.ordering} onChange={(e) => setFilters({ ...filters, ordering: e.target.value })}><option value="">پیش‌فرض</option><option value="price">کمترین قیمت</option><option value="-price">بیشترین قیمت</option></select><span>{currency.format(total)} آیتم</span></div></div>; }
function ProductCard({ product, index, onAdd, onOpen }) { return <article className="product-card"><button className="image-button" onClick={onOpen}><img src={mediaUrl(product.image, product.id || index)} alt={product.name} onError={(e) => { e.currentTarget.src = fallbackImage(index); }} /></button><div className="card-body"><div><button className="category-link" onClick={onOpen}>{product.category?.title || "Bakery"}</button><h3>{product.name}</h3></div></div><p className="description">{product.description || "محصول تازه و آماده سفارش."}</p><div className="card-footer"><strong>{currency.format(product.price)} تومان</strong><button onClick={() => onAdd(product)} disabled={product.inventory < 1 || product.is_available === false}><Plus size={18} /> افزودن</button></div></article>; }
function CartDrawer({ cart, onClose, onUpdate, onCheckout }) { return <div className="drawer-backdrop" onClick={onClose}><aside className="cart-drawer" onClick={(e) => e.stopPropagation()}><div className="drawer-head"><h2>سبد خرید</h2><button className="icon-button" onClick={onClose}><X size={20} /></button></div><div className="drawer-list">{!cart?.items?.length ? <div className="empty-state"><ShoppingCart size={40} />سبد خرید خالی است.</div> : cart.items.map((item) => <div key={item.id} className="cart-line"><div><strong>{item.product.name}</strong><span>{currency.format(item.sub_total)} تومان</span></div><div className="qty"><button onClick={() => onUpdate(item, item.quantity + 1)}><Plus size={15} /></button><b>{currency.format(item.quantity)}</b><button onClick={() => onUpdate(item, item.quantity - 1)}><Minus size={15} /></button><button onClick={() => onUpdate(item, 0)}><Trash2 size={16} /></button></div></div>)}</div><div className="drawer-foot"><div><span>جمع کل</span><strong>{currency.format(cart?.grand_total || 0)} تومان</strong></div><button className="dark-action" onClick={onCheckout}><PackageCheck size={19} /> ثبت سفارش</button></div></aside></div>; }
function CheckoutPage({ cart, loadCart, setView, setNotice }) { const [profile, setProfile] = useState(null); const [addresses, setAddresses] = useState([]); const [address, setAddress] = useState(null); const [discount, setDiscount] = useState(""); const [discountOk, setDiscountOk] = useState(null); const [busy, setBusy] = useState(false); useEffect(() => { request("/profile/").then(setProfile).catch((e) => setNotice(e.message)); loadAddresses(); }, []); async function loadAddresses() { const list = await request("/addresses/"); setAddresses(list); setAddress(null); } async function validateDiscount() { if (!discount.trim()) { setDiscountOk(null); return; } try { const data = await request("/discounts/validate/", { method: "POST", body: JSON.stringify({ code: discount }) }); setDiscountOk(data); setNotice(data.message); } catch (e) { setDiscountOk(null); setNotice(e.message); } } async function updateCheckoutItem(item, quantity) { try { if (quantity < 1) await request(`/carts/${cart.id}/items/${item.id}/`, { method: "DELETE" }); else await request(`/carts/${cart.id}/items/${item.id}/`, { method: "PATCH", body: JSON.stringify({ quantity }) }); await loadCart(); } catch (e) { setNotice(e.message); } } async function pay() { const selected = addresses.find((a) => a.id === address); if (!profile?.first_name || !profile?.last_name || !profile?.email || !profile?.phone) { setNotice("برای پرداخت ابتدا پروفایل را کامل کنید."); return; } if (!address || !selected || !isCompleteAddress(selected)) { setNotice("برای پرداخت باید یک آدرس کامل را انتخاب کنید."); return; } setBusy(true); try { const order = await request("/orders/", { method: "POST", body: JSON.stringify({ cart_id: cart.id, address_id: address, discount_code: discount }) }); await loadCart(); setNotice(`سفارش شماره ${order.id} با موفقیت پرداخت شد.`); setView("home"); window.scrollTo({ top: 0, behavior: "smooth" }); } catch (e) { setNotice(e.message); } finally { setBusy(false); } } const total = Number(cart?.grand_total || 0); const discountAmount = discountOk?.valid ? total * (discountOk.discount_percentage / 100) : 0; const canPay = Boolean(address && profile?.first_name && profile?.last_name && profile?.email && profile?.phone && addresses.find((a) => a.id === address && isCompleteAddress(a))); return <section className="checkout-page"><div className="checkout-head"><button onClick={() => setView("home")}><Home size={18} /> صفحه اصلی</button><h1>تکمیل سفارش</h1></div><div className="checkout-grid"><div className="checkout-panel"><h2>پروفایل</h2>{profile ? <ProfileEditor profile={profile} setProfile={setProfile} setNotice={setNotice} /> : <p>در حال دریافت پروفایل...</p>}<h2>آدرس ارسال</h2><p className="checkout-warning">برای فعال شدن پرداخت باید یکی از آدرس‌های کامل زیر را انتخاب کنید.</p><AddressManager addresses={addresses} selected={address} setSelected={setAddress} reload={loadAddresses} setNotice={setNotice} /></div><div className="checkout-panel"><h2>لیست محصولات</h2>{cart?.items?.map((item) => <div className="order-row checkout-item" key={item.id}><span>{item.product.name}</span><div className="qty"><button onClick={() => updateCheckoutItem(item, item.quantity + 1)}><Plus size={15} /></button><b>{currency.format(item.quantity)}</b><button onClick={() => updateCheckoutItem(item, item.quantity - 1)}><Minus size={15} /></button></div><strong>{currency.format(item.sub_total)} تومان</strong></div>)}<div className="discount-line"><input value={discount} onChange={(e) => setDiscount(e.target.value.toUpperCase())} placeholder="کد تخفیف" /><button onClick={validateDiscount}>بررسی</button></div><div className="totals"><span>جمع کل <b>{currency.format(total)} تومان</b></span><span>تخفیف <b>{currency.format(discountAmount)} تومان</b></span><strong>قابل پرداخت <b>{currency.format(total - discountAmount)} تومان</b></strong></div><button className="dark-action pay-button" onClick={pay} disabled={busy || !canPay}><CreditCard size={19} /> {busy ? "در حال پرداخت..." : "پرداخت و ثبت سفارش"}</button></div></div></section>; }
function isCompleteAddress(a) { return Boolean(a?.title?.trim() && a?.state?.trim() && a?.city?.trim() && a?.full_address?.trim() && /^\d{10}$/.test(a?.postal_code || "")); }
function ProfileEditor({ profile, setProfile, setNotice }) { async function save() { try { const saved = await request("/profile/update/", { method: "PATCH", body: JSON.stringify(profile) }); setProfile(saved); setNotice("پروفایل ذخیره شد."); } catch (e) { setNotice(e.message); } } return <div className="form-grid"><input value={profile.first_name || ""} onChange={(e) => setProfile({ ...profile, first_name: e.target.value })} placeholder="نام" /><input value={profile.last_name || ""} onChange={(e) => setProfile({ ...profile, last_name: e.target.value })} placeholder="نام خانوادگی" /><input value={profile.email || ""} onChange={(e) => setProfile({ ...profile, email: e.target.value })} placeholder="ایمیل" /><input value={profile.phone || ""} onChange={(e) => setProfile({ ...profile, phone: e.target.value })} placeholder="موبایل" /><button onClick={save}><Check size={17} /> ذخیره پروفایل</button></div>; }
function AddressManager({ addresses, selected, setSelected, reload, setNotice }) { const [form, setForm] = useState({ title: "", state: "", city: "", full_address: "", postal_code: "", is_default: false }); async function addAddress() { if (!isCompleteAddress(form)) { setNotice("همه فیلدهای آدرس و کدپستی ۱۰ رقمی را کامل کنید."); return; } try { await request("/addresses/", { method: "POST", body: JSON.stringify(form) }); setForm({ title: "", state: "", city: "", full_address: "", postal_code: "", is_default: false }); await reload(); setNotice("آدرس ذخیره شد."); } catch (e) { setNotice(e.message); } } return <div><div className="address-list">{addresses.map((item) => <button key={item.id} className={selected === item.id ? "selected" : ""} onClick={() => setSelected(item.id)}><MapPin size={17} /><span>{item.title} - {item.state}، {item.city}</span>{!isCompleteAddress(item) && <small>ناقص</small>}</button>)}</div>{addresses.length < 5 && <div className="form-grid address-form"><input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="عنوان آدرس" /><input value={form.state} onChange={(e) => setForm({ ...form, state: e.target.value })} placeholder="استان" /><input value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} placeholder="شهر" /><input value={form.postal_code} onChange={(e) => setForm({ ...form, postal_code: e.target.value })} placeholder="کد پستی ۱۰ رقمی" /><textarea value={form.full_address} onChange={(e) => setForm({ ...form, full_address: e.target.value })} placeholder="آدرس کامل" /><button onClick={addAddress}><Plus size={17} /> افزودن آدرس</button></div>}</div>; }
function ProfileModal({ onClose, setNotice }) { const [tab, setTab] = useState("profile"); const [profile, setProfile] = useState(null); const [addresses, setAddresses] = useState([]); const [orders, setOrders] = useState([]); const [cart, setCart] = useState(null); useEffect(() => { request("/profile/").then(setProfile).catch((e) => setNotice(e.message)); reload(); }, []); async function reload() { setAddresses(await request("/addresses/")); setOrders(normalizeList(await request("/orders/"))); setCart(await request("/carts/current/")); } return <div className="modal-backdrop" onClick={onClose}><section className="profile-panel" onClick={(e) => e.stopPropagation()}><button className="icon-button close" onClick={onClose}><X size={20} /></button><h2>پروفایل من</h2><div className="profile-tabs"><button className={tab === "profile" ? "active" : ""} onClick={() => setTab("profile")}>ویرایش پروفایل</button><button className={tab === "addresses" ? "active" : ""} onClick={() => setTab("addresses")}>آدرس‌ها</button><button className={tab === "orders" ? "active" : ""} onClick={() => setTab("orders")}>لیست خرید</button></div>{tab === "profile" && profile && <ProfileEditor profile={profile} setProfile={setProfile} setNotice={setNotice} />}{tab === "addresses" && <AddressManager addresses={addresses} selected={null} setSelected={() => {}} reload={reload} setNotice={setNotice} />}{tab === "orders" && <div className="history"><h3>پرداخت‌شده‌ها</h3>{orders.length ? orders.map((o) => <div key={o.id} className="history-row"><b>سفارش {o.id}</b><span>{currency.format(o.final_amount)} تومان</span><small>{o.items?.length || 0} محصول</small></div>) : <p>هنوز سفارشی پرداخت نشده است.</p>}<h3>سبد فعلی برای پرداخت بعدی</h3>{cart?.items?.length ? cart.items.map((i) => <div key={i.id} className="history-row"><b>{i.product.name}</b><span>{currency.format(i.sub_total)} تومان</span><small>{currency.format(i.quantity)} عدد</small></div>) : <p>سبد فعلی خالی است.</p>}</div>}</section></div>; }
function AuthModal({ onClose, onDone, setNotice }) { const [mode, setMode] = useState("login"); const [form, setForm] = useState({ first_name: "", last_name: "", phone: "", email: "", password: "", password2: "" }); const [busy, setBusy] = useState(false); async function submit(e) { e.preventDefault(); setBusy(true); try { if (mode === "register") { await request("/register/", { method: "POST", body: JSON.stringify(form) }); setMode("login"); setNotice("ثبت‌نام انجام شد. حالا وارد شوید."); } else { const data = await request("/login/", { method: "POST", body: JSON.stringify({ email: form.email, password: form.password }) }); localStorage.setItem("access_token", data.data.access_token); localStorage.setItem("refresh_token", data.data.refresh_token); setNotice("ورود موفق بود."); onDone(); } } catch (error) { setNotice(error.message); } finally { setBusy(false); } } return <div className="modal-backdrop" onClick={onClose}><form className="auth-card" onSubmit={submit} onClick={(e) => e.stopPropagation()}><button type="button" className="icon-button close" onClick={onClose}><X size={20} /></button><h2>{mode === "login" ? "ورود به حساب" : "ثبت‌نام"}</h2><div className="segments"><button type="button" className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>ورود</button><button type="button" className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>ثبت‌نام</button></div>{mode === "register" && <><input placeholder="نام" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} required /><input placeholder="نام خانوادگی" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} required /><input placeholder="موبایل" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} required /></>}<input type="email" placeholder="ایمیل" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required /><input type="password" placeholder="رمز عبور" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />{mode === "register" && <input type="password" placeholder="تکرار رمز عبور" value={form.password2} onChange={(e) => setForm({ ...form, password2: e.target.value })} required />}<button className="dark-action" disabled={busy}><LogIn size={18} />{busy ? "در حال ارسال..." : mode === "login" ? "ورود" : "ایجاد حساب"}</button></form></div>; }
function Toast({ message, onClose }) { useEffect(() => { const timer = setTimeout(onClose, 4500); return () => clearTimeout(timer); }, [message]); return <div className="toast">{message}</div>; }

createRoot(document.getElementById("root")).render(<App />);
