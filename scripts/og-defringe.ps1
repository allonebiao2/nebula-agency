# Defringe : detecte les bandes noires haut/bas (screenshots iPhone) et les
# remplace par du blanc, puis normalise en 600x800 (3:4) JPEG q78
# (norme NEBULA pour les photos produits).
#
# Algo de detection :
#   Pour chaque ligne y, on echantillonne les pixels au CENTRE (60% central
#   pour eviter les artefacts de bord) et on regarde si la ligne est
#   majoritairement noire (luminance moyenne < seuil).
#   On scanne du haut vers le bas pour trouver la 1re ligne non-noire,
#   idem du bas vers le haut.
#
# Usage : powershell -File scripts/og-defringe.ps1 <in.png|jpg> <out.jpg>

param(
  [Parameter(Mandatory=$true)][string]$InPath,
  [Parameter(Mandatory=$true)][string]$OutPath,
  [int]$DarkThresh = 60,           # ligne consideree noire si luminance moyenne < 60
  [double]$ContentRatio = 0.5,     # >= 50% de pixels clairs requis pour content line
  [int]$OutW = 600,
  [int]$OutH = 800,
  [int]$JpegQuality = 78
)

Add-Type -AssemblyName System.Drawing

$inFull = (Resolve-Path -LiteralPath $InPath).Path
$img = [System.Drawing.Image]::FromFile($inFull)
$srcW = $img.Width; $srcH = $img.Height
Write-Output ("Source : {0}x{1}" -f $srcW, $srcH)

# Convertir en 24bpp pour avoir des canaux RGB sans alpha
$bmp = New-Object System.Drawing.Bitmap $srcW, $srcH, ([System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.Clear([System.Drawing.Color]::White)
$g.DrawImage($img, 0, 0, $srcW, $srcH)
$g.Dispose()
$img.Dispose()

# LockBits pour scanner
$rect = New-Object System.Drawing.Rectangle 0, 0, $srcW, $srcH
$data = $bmp.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::ReadOnly, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
$stride = $data.Stride
$buf = New-Object byte[] ($stride * $srcH)
[System.Runtime.InteropServices.Marshal]::Copy($data.Scan0, $buf, 0, $buf.Length)
$bmp.UnlockBits($data)

# Zone centrale de scan (60% central de la largeur)
$scanFromX = [int]($srcW * 0.2)
$scanToX = [int]($srcW * 0.8)

function Test-LineIsContent($y) {
  $light = 0; $total = 0
  for ($x = $scanFromX; $x -lt $scanToX; $x++) {
    $i = ($y * $stride) + ($x * 3)
    # BGR order
    $b = $buf[$i]; $g2 = $buf[$i+1]; $r = $buf[$i+2]
    # Luminance approchee
    $lum = (0.299 * $r + 0.587 * $g2 + 0.114 * $b)
    if ($lum -gt $DarkThresh) { $light++ }
    $total++
  }
  return ($light / $total) -ge $ContentRatio
}

# Scan top
$top = 0
for ($y = 0; $y -lt $srcH; $y++) {
  if (Test-LineIsContent $y) { $top = $y; break }
}
# Scan bottom
$bottom = $srcH - 1
for ($y = $srcH - 1; $y -ge 0; $y--) {
  if (Test-LineIsContent $y) { $bottom = $y; break }
}
$bmp.Dispose()

Write-Output ("Crop vertical : y={0} -> y={1} (perte top={2}, bottom={3})" -f $top, $bottom, $top, ($srcH - 1 - $bottom))

# Reload pour cropper (System.Drawing easier que LockBits ici)
$img2 = [System.Drawing.Image]::FromFile($inFull)
$croppedH = $bottom - $top + 1
$cropRect = New-Object System.Drawing.Rectangle 0, $top, $srcW, $croppedH

# Cree un bitmap "intermediaire" : on copie la zone croppee SUR FOND BLANC
# (au cas ou la zone "content" contient encore des pixels noirs residuels sur les bords)
$inter = New-Object System.Drawing.Bitmap $srcW, $croppedH, ([System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
$g3 = [System.Drawing.Graphics]::FromImage($inter)
$g3.Clear([System.Drawing.Color]::White)
$g3.DrawImage($img2, (New-Object System.Drawing.Rectangle 0, 0, $srcW, $croppedH), $cropRect, [System.Drawing.GraphicsUnit]::Pixel)
$g3.Dispose()
$img2.Dispose()

Write-Output ("Apres crop : {0}x{1} (ratio {2:F2})" -f $srcW, $croppedH, ($srcW / [double]$croppedH))

# Maintenant, ajuster au ratio 3:4 (600/800 = 0.75)
$targetRatio = $OutW / [double]$OutH  # 0.75
$currentRatio = $srcW / [double]$croppedH

if ($currentRatio -gt $targetRatio) {
  # Trop large -> on ajoute du padding blanc en haut/bas
  $newH = [int]($srcW / $targetRatio)
  $padTopBot = [int](($newH - $croppedH) / 2)
  $padded = New-Object System.Drawing.Bitmap $srcW, $newH, ([System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
  $g4 = [System.Drawing.Graphics]::FromImage($padded)
  $g4.Clear([System.Drawing.Color]::White)
  $g4.DrawImage($inter, 0, $padTopBot)
  $g4.Dispose()
  $inter.Dispose()
  $inter = $padded
  Write-Output ("Pad vertical (image trop large) : nouveau {0}x{1}" -f $inter.Width, $inter.Height)
} elseif ($currentRatio -lt $targetRatio) {
  # Trop haute -> on ajoute du padding blanc gauche/droite
  $newW = [int]($croppedH * $targetRatio)
  $padLR = [int](($newW - $srcW) / 2)
  $padded = New-Object System.Drawing.Bitmap $newW, $croppedH, ([System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
  $g4 = [System.Drawing.Graphics]::FromImage($padded)
  $g4.Clear([System.Drawing.Color]::White)
  $g4.DrawImage($inter, $padLR, 0)
  $g4.Dispose()
  $inter.Dispose()
  $inter = $padded
  Write-Output ("Pad horizontal (image trop haute) : nouveau {0}x{1}" -f $inter.Width, $inter.Height)
}

# Resize final a OutW x OutH avec interpolation de qualite
$final = New-Object System.Drawing.Bitmap $OutW, $OutH, ([System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
$g5 = [System.Drawing.Graphics]::FromImage($final)
$g5.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g5.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
$g5.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
$g5.Clear([System.Drawing.Color]::White)
$g5.DrawImage($inter, 0, 0, $OutW, $OutH)
$g5.Dispose()
$inter.Dispose()

# Save JPEG q78
$jpegEncoder = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
$encParams = New-Object System.Drawing.Imaging.EncoderParameters(1)
$encParams.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter([System.Drawing.Imaging.Encoder]::Quality, [long]$JpegQuality)
$outFull = $OutPath
if (-not [System.IO.Path]::IsPathRooted($outFull)) { $outFull = Join-Path (Get-Location) $outFull }
$final.Save($outFull, $jpegEncoder, $encParams)
$final.Dispose()

$size = (Get-Item $outFull).Length
Write-Output ("Output : {0} ({1:F1} KB, {2}x{3}, JPEG q{4})" -f $outFull, ($size/1024), $OutW, $OutH, $JpegQuality)
