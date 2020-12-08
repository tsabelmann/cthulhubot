# Cthulhu Discord Bot
An interactive discord bot that allows convenient commands for dice throwing considering the pen and paper game **Cthulhu**.

## Installation

1. ```bash
   git clone https://github.com/tsabelmann/cthulhu_discord_bot
   ```
2. ```bash
   cd cthulhu_discord_bot
   ```
3. ```bash
   poetry install
   ```
4. ```bash
   echo "export DISCORD_TOKEN=YOUR_TOKEN" > .env
   ```
5. ```bash
   poetry run cthulhu
   ```

## Usage
The **Cthulhu** discord bot provides two commands: **#roll** and **#probe**. The **#roll** command allows the throwing of dice and the subsequent summation and addition of optional values. The **#probe** command allows the check of ones *ability* against **one** thrown <u>d100</u> with *additional* **bonus** or **malus** dice.

## Dice Syntax

A regular die is specified be the *amount* of dice you want to throw and the *dice eyes*. The most common dice eyes are **100**, **20**, **12**, **10**, **8**, **6**, **4**, and **3**.

### Examples

- `1d100`
- `2d100`
- `1d20`
- 3d10
- 1d8
- 6d6
- 1d4
- 2d3

## Value Syntax

Values to be added to the final sum consists of a *sign* and a *value* part.

### Examples

- `+2`
- `-3`

## Examples

- `#roll 1d100`
- `#roll 2d100 1d10 1d8 1d6 1d4 1d3`
- `#roll 1d20 +3`
- `#roll 1d20 +1+2+3`
- `#probe 50 \\ neither bonus nor malus is applied`
- `#probe 50 b 1`
- `#probe 50 B 1`
- `#probe 50 bon 1`
- `#probe 50 bonus 1`
- `#probe 50 m 1`
- `#probe 50 M 1`
- `#probe 50 mal 1`
- `#probe 50 malus 1`

## Acknowledgement

The bot is currently only available if one executes it on the fly. It is not containerized at the moment. Furthermore, the installation requires `Poetry`.