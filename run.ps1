if (-not (Test-Path -Path ".venv"))
{
    python -m venv ./.venv
}
./.venv/Scripts/Activate.ps1
pip install -r requirements1.txt

docker run -v ${PWD}:/sources ethereum/solc:0.8.18 -o /sources/output --abi --bin --overwrite /sources/order.sol

docker run --detach --publish 8545:8545 trufflesuite/ganache-cli:latest --accounts 10
python initOwner.py

docker build -f identity.dockerfile --tag identity:latest .
docker build -f identityinit.dockerfile --tag identityinit:latest .
docker build -f owner.dockerfile --tag owner:latest .
docker build -f customer.dockerfile --tag customer:latest .
docker build -f courier.dockerfile --tag courier:latest .
docker build -f storeinit.dockerfile --tag storeinit:latest .

docker-compose -f deploy.yaml up -d