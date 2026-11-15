'use strict';
const $ = id => document.getElementById(id);
let records = [], lowOnly = false, editing = null;
const notice = (message, error = false) => { $('notice').textContent = message; $('notice').className = error ? 'error' : ''; };
async function api(path, options = {}) {
  const response = await fetch(path, {...options, headers: {'Content-Type': 'application/json', ...(options.method ? {Authorization: `Bearer ${$('token').value.trim()}`} : {})}});
  if (response.status === 204) return null;
  const result = await response.json();
  if (!response.ok) throw new Error(response.status === 401 ? 'Write access denied. Enter the current API token below.' : result.error || `Request failed (${response.status})`);
  return result;
}
function cell(row, value) { const td = document.createElement('td'); td.textContent = value; row.append(td); return td; }
function render() {
  $('total').textContent = records.length;
  $('units').textContent = records.reduce((sum, item) => sum + item.quantity, 0).toLocaleString();
  $('low').textContent = records.filter(item => item.quantity < 5).length;
  $('empty').textContent = records.filter(item => item.quantity === 0).length;
  const query = $('search').value.trim().toLowerCase();
  const shown = records.filter(item => (!lowOnly || item.quantity < 5) && `${item.name} ${item.sku}`.toLowerCase().includes(query));
  $('rows').replaceChildren();
  for (const item of shown) {
    const row = document.createElement('tr');
    cell(row, item.name); cell(row, item.sku); cell(row, item.quantity.toLocaleString());
    const badge = document.createElement('span');
    badge.className = `badge ${item.quantity === 0 ? 'zero' : item.quantity < 5 ? 'low' : ''}`;
    badge.textContent = item.quantity === 0 ? 'Out of stock' : item.quantity < 5 ? 'Low stock' : 'In stock';
    cell(row, '').append(badge);
    const actions = cell(row, ''); actions.className = 'right';
    for (const [label, fn] of [['Update', () => openEditor(item)], ['Delete', () => remove(item)]]) {
      const button = document.createElement('button'); button.textContent = label;
      button.className = `action ${label === 'Delete' ? 'delete' : ''}`;
      button.setAttribute('aria-label', `${label} ${item.name}`); button.onclick = fn; actions.append(button);
    }
    $('rows').append(row);
  }
  $('empty-state').hidden = shown.length > 0;
  $('empty-state').textContent = records.length ? 'No items match this view.' : 'No items yet. Add your first item to get started.';
  $('count').textContent = `${shown.length} of ${records.length} items shown`;
  $('all').classList.toggle('selected', !lowOnly); $('filter').classList.toggle('selected', lowOnly);
  $('all').setAttribute('aria-pressed', !lowOnly); $('filter').setAttribute('aria-pressed', lowOnly);
}
async function refresh() {
  $('refresh').disabled = true;
  try {
    const [items, version] = await Promise.all([api('/items'), api('/version')]);
    records = items; render();
    $('version').textContent = `${version.version} · Revision ${version.revision.slice(0, 7)}`;
    $('updated').textContent = `Updated ${new Date().toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}`;
    await api('/ready'); $('connection').textContent = 'Service ready'; $('connection').className = 'connection ok';
  } catch (error) { $('connection').textContent = 'Service unavailable'; $('connection').className = 'connection bad'; notice(error.message, true); }
  finally { $('refresh').disabled = false; }
}
function openEditor(item = null) {
  editing = item; $('editor-title').textContent = item ? 'Update quantity' : 'Add inventory item';
  $('name').value = item?.name || ''; $('sku').value = item?.sku || ''; $('quantity').value = item?.quantity ?? 0;
  $('name').disabled = $('sku').disabled = Boolean(item); $('form-error').textContent = '';
  $('editor').showModal(); (item ? $('quantity') : $('name')).focus();
}
$('item-form').onsubmit = async event => {
  event.preventDefault();
  const quantity = Number($('quantity').value);
  if (!Number.isInteger(quantity) || quantity < 0 || quantity > 2147483647) { $('form-error').textContent = 'Quantity must be a whole number from 0 to 2147483647.'; return; }
  $('save').disabled = true;
  try {
    await api(editing ? `/items/${editing.id}` : '/items', {method: editing ? 'PATCH' : 'POST', body: JSON.stringify(editing ? {quantity} : {name: $('name').value, sku: $('sku').value, quantity})});
    $('editor').close(); notice(editing ? 'Quantity updated.' : 'Item added.'); await refresh();
  } catch (error) { $('form-error').textContent = error.message; }
  finally { $('save').disabled = false; }
};
async function remove(item) {
  if (!confirm(`Delete ${item.name}? This removes the inventory record.`)) return;
  try { await api(`/items/${item.id}`, {method: 'DELETE'}); notice('Item deleted.'); await refresh(); }
  catch (error) { notice(error.message, true); }
}
$('add').onclick = () => openEditor(); $('refresh').onclick = refresh;
$('all').onclick = () => { lowOnly = false; render(); }; $('filter').onclick = () => { lowOnly = true; render(); };
$('search').oninput = render; $('clear-token').onclick = () => { $('token').value = ''; notice('API token cleared.'); };
$('cancel').onclick = $('close-editor').onclick = () => $('editor').close();
refresh();
