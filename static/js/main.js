const filtroSetor = document.getElementById('filtroSetor');
const filtroTipo = document.getElementById('filtroTipo');
const tbody = document.getElementById('equipamento-tbody');

async function carregarSetores() {
  const res = await fetch('/setores');
  const setores = await res.json();
  setores.forEach(setor => {
    const option = document.createElement('option');
    option.value = setor;
    option.textContent = setor;
    filtroSetor.appendChild(option);
  });
}

async function carregarEquipamentos() {
  let url = '/equipamentos?';
  if (filtroSetor.value) url += `setor=${encodeURIComponent(filtroSetor.value)}&`;
  if (filtroTipo.value) url += `tipo=${encodeURIComponent(filtroTipo.value)}`;

  const res = await fetch(url);
  const equipamentos = await res.json();

  tbody.innerHTML = '';
  equipamentos.forEach(e => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${e.id}</td>
      <td>${e.tipo}</td>
      <td>${e.patrimonio_arklok}</td>
      <td>${e.setor}</td>
      <td>${e.hostname || ''}</td>
    `;
    tbody.appendChild(tr);
  });
}

function filtrar() {
  carregarEquipamentos();
}

function gerarRelatorioPdf() {
  let url = '/relatorio_pdf?';
  if (filtroSetor.value) url += `setor=${encodeURIComponent(filtroSetor.value)}&`;
  if (filtroTipo.value) url += `tipo=${encodeURIComponent(filtroTipo.value)}`;
  window.open(url, '_blank');
}

window.onload = () => {
  carregarSetores();
  carregarEquipamentos();

  filtroSetor.addEventListener('change', filtrar);
  filtroTipo.addEventListener('change', filtrar);

  const btnGerarPdf = document.getElementById('btnGerarPdf');
  if (btnGerarPdf) {
    btnGerarPdf.addEventListener('click', gerarRelatorioPdf);
  }
};
