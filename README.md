# InfraScore JP

[![Tests](https://github.com/yorosiku008/infrascore-cli/actions/workflows/test.yml/badge.svg)](https://github.com/yorosiku008/infrascore-cli/actions)
[![Beta](https://img.shields.io/badge/β版-募集中-brightgreen)](https://github.com/yorosiku008/infrascore-cli/issues/new?template=beta_application.md&title=%5Bβ版申込%5D)

AWSインフラ健全性スコアリングCLI — 可用性・パフォーマンス・セキュリティ・コスト効率を100点満点で評価します。

## インストール

```bash
git clone https://github.com/yorosiku008/infrascore-cli.git
cd infrascore-cli
pip install -r requirements.txt
```

## 使い方

```bash
# デモデータで動作確認（AWS不要）
python main.py --demo

# 実環境スキャン
python main.py --profile default

# Markdownレポートも保存
python main.py --profile default --output-md
```

## スコアリング軸

| 軸 | 重み | 評価内容 |
|---|---|---|
| 可用性 | 35% | CloudWatchアラート / ELB 5xxエラー率 / RDS可用性 |
| パフォーマンス | 25% | CPU使用率 / メモリ使用率 / p95レイテンシ |
| セキュリティ | 25% | 危険ポート開放 / MFA設定 / S3暗号化 |
| コスト効率 | 15% | RIカバレッジ / アイドルEC2 / 未アタッチEBS |

**グレード:** S(90+) / A(80+) / B(70+) / C(60+) / D(50+) / E(0+)

## テスト

```bash
pytest tests/ -v
# 30 passed
```

## 必要なAWS権限

```
cloudwatch:DescribeAlarms
cloudwatch:GetMetricStatistics
ec2:DescribeSecurityGroups
ec2:DescribeVolumes
s3:ListBuckets
s3:GetBucketEncryption
```

---

*InfraScore JP v0.1.0 — β版ユーザー募集中: yorosiku008.github.io/infrascore-lp/*
