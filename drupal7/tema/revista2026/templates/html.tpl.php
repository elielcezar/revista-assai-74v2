<?php
/**
 * @file
 * Documento da Revista 2026. Mesma ordem do <head> do protótipo: GTM logo
 * depois do charset, viewport, anti-piscada, título, CSS. Os CSS e JS do tema
 * saem direto aqui, sem a agregação do Drupal: a ordem importa e o
 * shell-desktop.js acha o gerador de QR pelo próprio endereço.
 */
?><!DOCTYPE html>
<html lang="pt-BR">
<head>
<?php print $head; ?>
<?php if ($revista): ?>
<?php print $revista['gtm']; ?>
<meta name="viewport" content="width=device-width, initial-scale=1">
<?php if ($revista['espera']) print $revista['espera'] . "\n"; ?>
<?php endif; ?>
<title><?php print $head_title; ?></title>
<?php print $styles; ?>
<?php if ($revista) print $revista['head'] . "\n"; ?>
<?php print $scripts; ?>
</head>
<body class="<?php print $classes; ?>" <?php print $attributes; ?>>
<?php print $page_top; ?>
<?php print $page; ?>
<?php print $page_bottom; ?>
<?php if ($revista) print $revista['scripts'] . "\n"; ?>
</body>
</html>
