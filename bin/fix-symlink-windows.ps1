# PowerShell script to find symlinks, convert them to windows symbolic links, and
# then ignore the change in .git. It will need to be run when you first clone,
# or when you checkout an older commit.

#Requires -RunAsAdministrator

$HuntPath = Join-Path $PSScriptRoot "..\"
$SourcePath = Join-Path $HuntPath "hunt\data\templates"

$Symlinks = @{round_files="../round"; puzzle_files="../puzzle"}

foreach ($h in $Symlinks.GetEnumerator()) {
	$Name = $h.Name;
	$Value = $h.Value;

	$Source = Join-Path $SourcePath $Name
	$SourceExists = (Test-Path $Source)

	Write-Host "Already exists?", $SourceExists
	if ($SourceExists) {
		$LinkType = (Get-Item $Source).LinkType
		Write-Host "Link type", $LinkType
		if ($LinkType -ne "SymbolicLink") {
			Write-Host "Removing git's symlink"
			Remove-Item $Source
		}
	}

	if (Test-Path $Source) {
		Write-Host "Symbolic link for $Name already exists, doing nothing"
	} else {
		Write-Host "Creating symbolic link"
		Push-Location $SourcePath
		New-Item -ItemType SymbolicLink -Name $Name -Value $Value
		Pop-Location

		Write-Host "Ignoring the change in git"
		Push-Location $HuntPath
		git update-index --assume-unchanged "hunt\data\templates\$Name"
		Pop-Location
	}
}
