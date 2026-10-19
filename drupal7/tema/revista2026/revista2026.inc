<?php
/**
 * @file
 * Revista 2026 — montagem da página a partir do corpo do conteúdo.
 *
 * Funções puras, sem chamadas ao Drupal: o template.php passa o corpo, as
 * listas de CSS/JS dos campos e uma função que transforma alias em link. O
 * drupal7/scripts/preview.php usa as mesmas funções para renderizar a página
 * fora do Drupal e comparar com o protótipo.
 *
 * O corpo começa com um comentário de controle, gerado pelo exportar.py:
 *
 *   <!-- revista2026 {"pagina": "74/gestao.html", "edicao": "74", ...} -->
 *
 * Campos do comentário (todos opcionais):
 *   pagina    arquivo de origem no protótipo (menu extra por página)
 *   edicao    "74", "73"... (texto da casca e links do menu); padrão: edicao_atual
 *   layout    "74" (o tema monta .page, cabeçalho e rodapé em volta do corpo)
 *             ou "73" (o corpo traz o <main> inteiro, com cabeçalho e rodapé
 *             próprios); padrão: "73" se o corpo tiver <main, senão "74"
 *   classe    classe extra do .page no layout 74 (capa, academia...)
 *   ativo     rótulo do item ativo no menu (GESTÃO, CAPA...)
 *   logo      imagem do logo do cabeçalho, quando não é a padrão
 *   descricao meta description
 *   fontes    endereço do Google Fonts da página (padrão: Inter 400/500/700)
 *   fx        true: carrega GSAP + ScrollTrigger + js/scroll-fx.js
 *   splittext true: carrega também o SplitText
 *   espera    seletores escondidos pelo trecho anti-piscada (efeitos de entrada)
 *
 * No layout 73, o marcador <!-- revista2026:menu --> dentro do corpo é
 * trocado pelos links do menu.
 */

define('REVISTA2026_GSAP', 'https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/');

function revista2026_e($s) {
  return htmlspecialchars((string) $s, ENT_QUOTES, 'UTF-8');
}

/**
 * Separa o comentário de controle do resto do corpo.
 *
 * @return array
 *   array($meta, $corpo)
 */
function revista2026_ler_corpo($corpo) {
  $meta = array();
  if (preg_match('/^\s*<!--\s*revista2026\s+(\{.*?\})\s*-->\s*/s', $corpo, $m)) {
    $lido = json_decode($m[1], TRUE);
    if (is_array($lido)) {
      $meta = $lido;
    }
    $corpo = substr($corpo, strlen($m[0]));
  }
  return array($meta, $corpo);
}

function revista2026_meta($meta, $chave, $padrao = NULL) {
  return isset($meta[$chave]) && $meta[$chave] !== '' ? $meta[$chave] : $padrao;
}

/**
 * Itens de um menu ('casca', 'head' ou 'menu73') para a página indicada.
 *
 * @return array
 *   lista de array('rotulo', 'alias' (ou NULL), 'cor', 'traco')
 */
function revista2026_menu($cfg, $pagina, $edicao, $onde) {
  $menu = $cfg['menu'];
  if ($pagina && isset($cfg['menu_extras'][$pagina])) {
    foreach ($cfg['menu_extras'][$pagina] as $extra) {
      $pos = count($menu);
      foreach ($menu as $i => $item) {
        if ($item['rotulo'] === $extra['antes']) {
          $pos = $i;
          break;
        }
      }
      array_splice($menu, $pos, 0, array($extra));
    }
  }
  $prefixo = isset($cfg['edicoes'][$edicao]['prefixo_menu']) ? $cfg['edicoes'][$edicao]['prefixo_menu'] : '';
  $itens = array();
  foreach ($menu as $item) {
    $lugares = isset($item['onde']) ? $item['onde'] : array('casca', 'head', 'menu73');
    if (!in_array($onde, $lugares, TRUE)) {
      continue;
    }
    $alias = NULL;
    if (!empty($item['pagina'])) {
      $chave = $item['pagina'];
      if (!empty($item['da_edicao']) && $prefixo && isset($cfg['paginas'][$prefixo . $chave])) {
        $chave = $prefixo . $chave;
      }
      $alias = isset($cfg['paginas'][$chave]) ? $cfg['paginas'][$chave] : '';
    }
    $itens[] = array(
      'rotulo' => $item['rotulo'],
      'alias' => $alias,
      'cor' => $item['cor'],
      'traco' => isset($item['traco']) ? $item['traco'] : '',
    );
  }
  return $itens;
}

function revista2026_href($item, $link) {
  if ($item['alias'] === NULL || $item['alias'] === '') {
    return '#';
  }
  return call_user_func($link, $item['alias']);
}

/**
 * Casca do desktop: o mesmo markup que o scripts/shell_sync.py gera no protótipo.
 */
function revista2026_casca($cfg, $meta, $ctx) {
  $edicao = revista2026_meta($meta, 'edicao', $cfg['edicao_atual']);
  $ed = isset($cfg['edicoes'][$edicao]) ? $cfg['edicoes'][$edicao] : $cfg['edicoes'][$cfg['edicao_atual']];
  $ativo = revista2026_meta($meta, 'ativo');
  $tema = $ctx['tema'];
  $v = '?v=' . $cfg['versao'];

  $l = array();
  $l[] = '<!-- ============ CASCA DESKTOP: tema revista2026 ============ -->';
  $l[] = '<div class="casca">';
  $l[] = '  <aside class="casca-esq" aria-label="Navegação da revista">';
  $l[] = '    <a class="casca-logo" href="' . revista2026_e($cfg['logo_site']) . '" target="_blank" rel="noopener"><img src="' . $tema . '/assets/shell/dt-logo-assai.png' . $v . '" alt="Assaí Atacadista" width="124" height="124"></a>';
  $l[] = '    <p class="casca-edicao">' . revista2026_e($ed['rotulo']) . '<br>' . revista2026_e($ed['data']) . '</p>';
  $l[] = '    <div class="casca-menu">';
  $l[] = '      <nav class="casca-nav" aria-label="Seções da revista">';
  foreach (revista2026_menu($cfg, revista2026_meta($meta, 'pagina'), $edicao, 'casca') as $item) {
    $a = $item['rotulo'] === $ativo ? ' class="is-active" aria-current="page"' : '';
    $l[] = '        <a href="' . revista2026_e(revista2026_href($item, $ctx['link'])) . '" target="_blank" rel="noopener" style="--mc:' . $item['cor'] . '"' . $a . '>' . revista2026_e($item['rotulo']) . '</a>';
  }
  $l[] = '      </nav>';
  $l[] = '      <a class="casca-pilula" href="' . revista2026_e($cfg['edicoes_anteriores']) . '" target="_blank" rel="noopener">Edições anteriores</a>';
  $l[] = '    </div>';
  $l[] = '  </aside>';
  $l[] = '  <aside class="casca-dir" aria-label="Assaí nas redes sociais">';
  $l[] = '    <p class="casca-siga">Siga o Assaí</p>';
  $l[] = '    <ul class="casca-redes">';
  foreach ($cfg['redes'] as $r) {
    $l[] = '      <li><a href="' . revista2026_e($r['url']) . '" target="_blank" rel="noopener" aria-label="Assaí no ' . revista2026_e($r['nome']) . '"><img src="' . $tema . '/assets/shell/rede-' . $r['icone'] . '.svg' . $v . '" alt="" width="' . (int) $r['w'] . '" height="' . (int) $r['h'] . '"></a></li>';
  }
  $l[] = '    </ul>';
  $l[] = '    <div class="casca-qr">';
  $l[] = '      <p class="casca-pilula">Ler no celular</p>';
  $l[] = '      <div class="casca-qr-img" role="img" aria-label="QR code com o endereço desta página"></div>';
  $l[] = '    </div>';
  $l[] = '  </aside>';
  $l[] = '</div>';
  $l[] = '<!-- ============ /CASCA DESKTOP ============ -->';
  return implode("\n", $l);
}

/**
 * Cabeçalho da #74 (COMPONENTE HEAD), com o menu horizontal do mobile.
 */
function revista2026_head74($cfg, $meta, $ctx) {
  $edicao = revista2026_meta($meta, 'edicao', $cfg['edicao_atual']);
  $ativo = revista2026_meta($meta, 'ativo');
  $logo = revista2026_meta($meta, 'logo', $ctx['tema'] . '/assets/imgLogoHead.svg?v=' . $cfg['versao']);

  $l = array();
  $l[] = '  <!-- ============ COMPONENTE HEAD ============ -->';
  $l[] = '  <header class="head">';
  $l[] = '    <div class="head-brand">';
  $l[] = '      <img class="head-logo" src="' . revista2026_e($logo) . '" alt="Assaí Bons Negócios" width="283" height="30">';
  $l[] = '    </div>';
  $l[] = '    <nav class="head-nav" aria-label="Seções da revista">';
  $l[] = '      <ul>';
  foreach (revista2026_menu($cfg, revista2026_meta($meta, 'pagina'), $edicao, 'head') as $item) {
    $li = ' style="--mc:' . $item['cor'] . '"';
    if ($item['alias'] === NULL) {
      $l[] = '        <li' . $li . '><a href="#">' . revista2026_e($item['rotulo']) . '</a></li>';
      continue;
    }
    $atual = '';
    if ($item['rotulo'] === $ativo) {
      $li .= ' class="is-active"';
      $atual = ' aria-current="page"';
    }
    $l[] = '        <li' . $li . '><a href="' . revista2026_e(revista2026_href($item, $ctx['link'])) . '"' . $atual . ' target="_blank" rel="noopener">' . revista2026_e($item['rotulo']) . '</a></li>';
  }
  $l[] = '      </ul>';
  $l[] = '    </nav>';
  $l[] = '  </header>';
  return implode("\n", $l);
}

/**
 * Rodapé da #74 (COMPONENTE RODAPE).
 */
function revista2026_foot74($cfg, $ctx) {
  $a = $ctx['tema'] . '/assets/';
  $v = '?v=' . $cfg['versao'];
  $l = array();
  $l[] = '  <!-- ============ COMPONENTE RODAPE ============ -->';
  $l[] = '  <footer class="foot">';
  $l[] = '    <span class="foot-bar" aria-hidden="true"></span>';
  $l[] = '    <a class="foot-top" href="#" aria-label="Voltar ao topo"><img src="' . $a . 'imgGroup8650.svg' . $v . '" alt=""></a>';
  $l[] = '    <button class="foot-share" type="button" aria-label="Compartilhar">';
  $l[] = '      <img class="foot-share-a" src="' . $a . 'imgGroup.svg' . $v . '" alt="">';
  $l[] = '      <img class="foot-share-b" src="' . $a . 'imgVector1.svg' . $v . '" alt="">';
  $l[] = '      <img class="foot-share-c" src="' . $a . 'imgVector2.svg' . $v . '" alt="">';
  $l[] = '    </button>';
  $l[] = '    <span class="foot-brand"><img src="' . $a . 'imgGroup2.svg' . $v . '" alt="Assaí Atacadista"></span>';
  $l[] = '    <a class="foot-stores" href="' . revista2026_e($cfg['nossas_lojas']) . '" target="_blank" rel="noopener noreferrer">NOSSAS LOJAS <img src="' . $a . 'imgGroup8651.svg' . $v . '" alt=""></a>';
  $l[] = '  </footer>';
  return implode("\n", $l);
}

/**
 * Links do menu do cabeçalho das páginas no shell da #73 (.head-menu-inner).
 */
function revista2026_menu73($cfg, $meta, $ctx) {
  $edicao = revista2026_meta($meta, 'edicao', $cfg['edicao_atual']);
  $ativo = revista2026_meta($meta, 'ativo');
  $l = array();
  foreach (revista2026_menu($cfg, revista2026_meta($meta, 'pagina'), $edicao, 'menu73') as $item) {
    $classe = trim($item['traco'] . ($item['rotulo'] === $ativo ? ' is-active' : ''));
    $l[] = '<a class="' . $classe . '" href="' . revista2026_e(revista2026_href($item, $ctx['link'])) . '" data-menu-item target="_blank" rel="noopener">' . revista2026_e($item['rotulo']) . '</a>';
  }
  return implode("\n", $l);
}

/**
 * Transforma o valor de um campo de CSS/JS em lista de endereços.
 *
 * Aceita, em cada item do campo: um endereço; vários, um por linha; ou tags
 * <link>/<script> coladas (lê o href/src). Caminho relativo (css/gestao.css)
 * é lido a partir da pasta da edição no FTP. "defer" depois de um endereço
 * (ou na tag <script>) carrega o script com defer, como no protótipo.
 *
 * @return array
 *   lista de array('url' => ..., 'defer' => TRUE/FALSE)
 */
function revista2026_urls($valores, $cfg, $edicao) {
  $ed = isset($cfg['edicoes'][$edicao]) ? $cfg['edicoes'][$edicao] : $cfg['edicoes'][$cfg['edicao_atual']];
  $base = rtrim($cfg['urls']['ftp'], '/') . '/' . $ed['pasta'] . '/';
  $itens = array();
  foreach ($valores as $valor) {
    if (strpos($valor, '<') !== FALSE) {
      preg_match_all('/<(?:link|script)\b[^>]*>/i', $valor, $tags);
      foreach ($tags[0] as $tag) {
        if (preg_match('/\b(?:href|src)\s*=\s*["\']([^"\']+)["\']/i', $tag, $m)) {
          $itens[] = array('url' => $m[1], 'defer' => (bool) preg_match('/\sdefer\b/i', $tag));
        }
      }
    }
    else {
      foreach (preg_split('/\s+/', trim($valor), -1, PREG_SPLIT_NO_EMPTY) as $parte) {
        if (strtolower($parte) === 'defer') {
          if ($itens) {
            $itens[count($itens) - 1]['defer'] = TRUE;
          }
          continue;
        }
        $itens[] = array('url' => $parte, 'defer' => FALSE);
      }
    }
  }
  foreach ($itens as &$item) {
    if (!preg_match('#^(?:[a-z]+:)?//#i', $item['url']) && $item['url'][0] !== '/') {
      $item['url'] = $base . preg_replace('#^(\./)+#', '', $item['url']);
    }
  }
  return $itens;
}

/**
 * Monta as partes da página.
 *
 * @param array $ctx
 *   tema: endereço da pasta do tema; link: função alias -> href;
 *   css, js: saída de revista2026_urls() para os campos do conteúdo.
 *
 * @return array
 *   layout, espera (anti-piscada), head (CSS e meta), corpo (dentro do
 *   <body>), scripts (fim do <body>), edicao.
 */
function revista2026_montar($cfg, $meta, $corpo, $ctx) {
  $layout = (string) revista2026_meta($meta, 'layout', preg_match('/<main\b/i', $corpo) ? '73' : '74');
  $edicao = revista2026_meta($meta, 'edicao', $cfg['edicao_atual']);
  $tema = $ctx['tema'];
  $v = '?v=' . $cfg['versao'];
  $fx = (bool) revista2026_meta($meta, 'fx', FALSE);

  // anti-piscada dos efeitos de entrada (ver a skill scroll-fx)
  $espera = '';
  if ($sel = revista2026_meta($meta, 'espera')) {
    $espera = "<!-- scroll-fx: esconde os efeitos de entrada antes da primeira pintura; o\n"
      . "     js/scroll-fx.js assume depois. Se ele não rodar, reaparecem em 3s. -->\n"
      . '<script>document.documentElement.classList.add("fx-espera");setTimeout(function(){document.documentElement.classList.remove("fx-espera")},3000);</script>' . "\n"
      . '<style>' . str_replace('</', '<\/', $sel) . '{visibility:hidden}</style>';
  }

  $head = array();
  if ($d = revista2026_meta($meta, 'descricao')) {
    $head[] = '<meta name="description" content="' . revista2026_e($d) . '">';
  }
  $head[] = '<link rel="preconnect" href="https://fonts.googleapis.com">';
  $head[] = '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>';
  $fontes = revista2026_meta($meta, 'fontes', 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');
  $head[] = '<link href="' . revista2026_e($fontes) . '" rel="stylesheet">';
  $css = array();
  foreach ($ctx['css'] as $u) {
    $css[] = '<link rel="stylesheet" href="' . revista2026_e($u['url']) . '">';
  }
  if ($layout === '73') {
    $head = array_merge($head, $css);
    $head[] = '<link rel="stylesheet" href="' . $tema . '/css/revista-73-shell.css' . $v . '">';
  }
  else {
    $head[] = '<link rel="stylesheet" href="' . $tema . '/css/base.css' . $v . '">';
    $head = array_merge($head, $css);
    $head[] = '<link rel="stylesheet" href="' . $tema . '/css/shell.css' . $v . '">';
  }
  $head[] = '<!-- casca do desktop: por último -->';
  $head[] = '<link rel="stylesheet" href="' . $tema . '/css/shell-desktop.css' . $v . '">';

  $js = array();
  foreach ($ctx['js'] as $u) {
    $js[] = '<script src="' . revista2026_e($u['url']) . '"' . ($u['defer'] ? ' defer' : '') . '></script>';
  }
  $scripts = array();
  $scripts[] = $layout === '73'
    ? '<script src="' . $tema . '/js/revista-73-menu.js' . $v . '" defer></script>'
    : '<script src="' . $tema . '/js/shell.js' . $v . '"></script>';
  $scripts = array_merge($scripts, $js);
  if ($fx) {
    $scripts[] = '<script src="' . REVISTA2026_GSAP . 'gsap.min.js"></script>';
    $scripts[] = '<script src="' . REVISTA2026_GSAP . 'ScrollTrigger.min.js"></script>';
    if (revista2026_meta($meta, 'splittext', FALSE)) {
      $scripts[] = '<script src="' . REVISTA2026_GSAP . 'SplitText.min.js"></script>';
    }
    $scripts[] = '<script src="' . $tema . '/js/scroll-fx.js' . $v . '"></script>';
  }
  $scripts[] = '<script src="' . $tema . '/js/shell-desktop.js' . $v . '"></script>';

  $casca = revista2026_casca($cfg, $meta, $ctx);
  if ($layout === '73') {
    $miolo = str_replace('<!-- revista2026:menu -->', revista2026_menu73($cfg, $meta, $ctx), $corpo);
  }
  else {
    $classe = revista2026_meta($meta, 'classe', '');
    $miolo = '<div class="page' . ($classe !== '' ? ' ' . revista2026_e($classe) : '') . '">' . "\n\n"
      . revista2026_head74($cfg, $meta, $ctx) . "\n\n"
      . $corpo . "\n\n"
      . revista2026_foot74($cfg, $ctx) . "\n\n"
      . '</div>';
  }

  return array(
    'layout' => $layout,
    'edicao' => $edicao,
    'espera' => $espera,
    'head' => implode("\n", $head),
    'corpo' => $casca . "\n\n" . $miolo,
    'scripts' => implode("\n", $scripts),
  );
}

/**
 * Título da aba: "<título do conteúdo> — Revista Assaí Bons Negócios #74",
 * a menos que o título já cite a revista.
 */
function revista2026_titulo($cfg, $titulo, $edicao) {
  if (stripos($titulo, $cfg['titulo_sufixo']) !== FALSE) {
    return $titulo;
  }
  return $titulo . ' — ' . $cfg['titulo_sufixo'] . ' #' . $edicao;
}

/**
 * Os dois contêineres do Google Tag Manager, como no protótipo.
 */
function revista2026_gtm($cfg) {
  $s = '';
  foreach ($cfg['gtm'] as $id) {
    $s .= "<!-- Google Tag Manager -->\n<script>\n(function(w,d,s,l,i){\n"
      . "  w[l]=w[l]||[];\n"
      . "  w[l].push({'gtm.start': new Date().getTime(),event:'gtm.js'});\n"
      . "  var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';\n"
      . "  j.async=true;\n"
      . "  j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;\n"
      . "  f.parentNode.insertBefore(j,f);\n"
      . "})(window,document,'script','dataLayer','" . revista2026_e($id) . "');\n</script>\n<!-- End Google Tag Manager -->\n";
  }
  return $s;
}
