<?php
/**
 * @file
 * Tema Revista 2026 (Drupal 7): ligação com o Drupal.
 *
 * A montagem da página fica em revista2026.inc. Aqui só se lê o conteúdo
 * (corpo + campos de CSS/JS), entrega as partes aos templates e limpa o CSS
 * do núcleo, que não pode interferir no layout do protótipo.
 */

require_once dirname(__FILE__) . '/revista2026.inc';

/**
 * Configuração do tema (revista.json).
 */
function revista2026_config() {
  $cfg = &drupal_static(__FUNCTION__);
  if (!isset($cfg)) {
    $arquivo = drupal_get_path('theme', 'revista2026') . '/revista.json';
    $cfg = json_decode(file_get_contents($arquivo), TRUE);
    if (!is_array($cfg)) {
      watchdog('revista2026', 'revista.json ilegível: @erro', array('@erro' => json_last_error_msg()), WATCHDOG_ERROR);
      $cfg = FALSE;
    }
  }
  return $cfg;
}

/**
 * Valores de um campo de texto/link do conteúdo, como strings.
 */
function revista2026_valores_do_campo($node, $campo) {
  $valores = array();
  if ($campo && ($itens = field_get_items('node', $node, $campo))) {
    foreach ($itens as $item) {
      if (isset($item['value'])) {
        $valores[] = $item['value'];
      }
      elseif (isset($item['url'])) {
        $valores[] = $item['url'];
      }
    }
  }
  return $valores;
}

function revista2026_link_drupal($alias) {
  return url($alias);
}

/**
 * Partes da página do conteúdo aberto, ou FALSE fora de um conteúdo da revista.
 */
function revista2026_dados() {
  $dados = &drupal_static(__FUNCTION__);
  if (isset($dados)) {
    return $dados;
  }
  $dados = FALSE;

  // só a visualização do conteúdo (node/N), não node/N/edit, revisões etc.
  $node = menu_get_object('node');
  if (!$node || arg(2) !== NULL || !($cfg = revista2026_config())) {
    return $dados;
  }
  $tipo = theme_get_setting('revista2026_tipo', 'revista2026');
  if ($tipo && $node->type !== $tipo) {
    return $dados;
  }
  $corpo = field_get_items('node', $node, 'body');
  if (!$corpo) {
    return $dados;
  }

  // O corpo é impresso como foi cadastrado, sem os filtros do formato de
  // texto: o "Full HTML" do Drupal troca quebras de linha por <p>/<br> e
  // corrige tags, o que desmonta o layout. Só quem cadastra conteúdo da
  // revista escreve aqui.
  list($meta, $html) = revista2026_ler_corpo($corpo[0]['value']);
  $edicao = revista2026_meta($meta, 'edicao', $cfg['edicao_atual']);
  $ctx = array(
    'tema' => base_path() . drupal_get_path('theme', 'revista2026'),
    'link' => 'revista2026_link_drupal',
    'css' => revista2026_urls(revista2026_valores_do_campo($node, theme_get_setting('revista2026_campo_css', 'revista2026')), $cfg, $edicao),
    'js' => revista2026_urls(revista2026_valores_do_campo($node, theme_get_setting('revista2026_campo_js', 'revista2026')), $cfg, $edicao),
  );
  $dados = revista2026_montar($cfg, $meta, $html, $ctx);
  $dados['titulo'] = revista2026_titulo($cfg, $node->title, $edicao);
  $dados['gtm'] = theme_get_setting('revista2026_gtm', 'revista2026') ? revista2026_gtm($cfg) : '';
  $dados['node'] = $node;
  return $dados;
}

/**
 * Implements template_preprocess_html().
 */
function revista2026_preprocess_html(&$vars) {
  $vars['revista'] = revista2026_dados();
  if ($vars['revista']) {
    $vars['head_title'] = check_plain($vars['revista']['titulo']);
  }
}

/**
 * Implements template_preprocess_page().
 */
function revista2026_preprocess_page(&$vars) {
  $vars['revista'] = revista2026_dados();
}

/**
 * Implements hook_css_alter().
 *
 * Na página da revista, tira o CSS do núcleo e dos módulos (system.menus,
 * node.css, field.css...). Para quem está logado, mantém o da barra de
 * administração.
 */
function revista2026_css_alter(&$css) {
  if (!revista2026_dados()) {
    return;
  }
  $admin = user_is_logged_in();
  foreach (array_keys($css) as $chave) {
    if (!$admin || !preg_match('#(toolbar|contextual|shortcut|admin_menu|system\.base)#', $chave)) {
      unset($css[$chave]);
    }
  }
}
