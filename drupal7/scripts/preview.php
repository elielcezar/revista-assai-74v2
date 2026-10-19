<?php
/**
 * @file
 * Renderiza os conteúdos exportados com o tema, fora do Drupal.
 *
 *   php drupal7/scripts/preview.php
 *
 * Usa o revista2026.inc e os templates do tema de drupal7/build/tema, com as
 * variáveis que o Drupal entregaria a um visitante anônimo (sem CSS/JS do
 * núcleo). Grava drupal7/build/preview/<alias>/index.html. O comparar.py serve
 * essa pasta como se fosse o site e compara cada página com o protótipo.
 */

$build = dirname(__DIR__) . '/build';
$tema_dir = $build . '/tema/revista2026';
require $tema_dir . '/revista2026.inc';

// o mínimo do Drupal que os templates usam
function check_plain($s) {
  return htmlspecialchars($s, ENT_QUOTES, 'UTF-8');
}
function render(&$x) {
  return is_string($x) ? $x : '';
}
function revista2026_link_preview($alias) {
  global $cfg;
  return rtrim($cfg['urls']['site'], '/') . '/' . $alias;
}

$cfg = json_decode(file_get_contents($tema_dir . '/revista.json'), TRUE);
$itens = json_decode(file_get_contents($build . '/conteudos/conteudos.json'), TRUE);

foreach ($itens as $n => $item) {
  list($meta, $corpo) = revista2026_ler_corpo(file_get_contents($build . '/' . $item['corpo']));
  $edicao = revista2026_meta($meta, 'edicao', $cfg['edicao_atual']);
  $revista = revista2026_montar($cfg, $meta, $corpo, array(
    'tema' => '/sites/all/themes/revista2026',
    'link' => 'revista2026_link_preview',
    'css' => revista2026_urls($item['css'], $cfg, $edicao),
    'js' => revista2026_urls($item['js'], $cfg, $edicao),
  ));
  $revista['gtm'] = revista2026_gtm($cfg);

  // page.tpl.php
  $messages = '';
  $tabs = array();
  $page = array('content' => '');
  ob_start();
  include $tema_dir . '/templates/page.tpl.php';
  $page = ob_get_clean();

  // html.tpl.php
  $head = '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />' . "\n";
  $head_title = check_plain(revista2026_titulo($cfg, $item['titulo'], $edicao));
  $styles = $scripts = $page_top = $page_bottom = $attributes = '';
  $classes = 'html not-front not-logged-in no-sidebars page-node page-node- page-node-' . ($n + 1) . ' node-type-revista-2026';
  ob_start();
  include $tema_dir . '/templates/html.tpl.php';
  $saida = ob_get_clean();

  $dest = $build . '/preview/' . $item['alias'] . '/index.html';
  if (!is_dir(dirname($dest))) {
    mkdir(dirname($dest), 0777, TRUE);
  }
  file_put_contents($dest, $saida);
}
echo count($itens) . " páginas em build/preview\n";
