// Copyright (c) 2011-2020 The QTY Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef QTY_QT_QTYADDRESSVALIDATOR_H
#define QTY_QT_QTYADDRESSVALIDATOR_H

#include <QValidator>

/** Base58 entry widget validator, checks for valid characters and
 * removes some whitespace.
 */
class QTYAddressEntryValidator : public QValidator
{
    Q_OBJECT

public:
    explicit QTYAddressEntryValidator(QObject *parent);

    State validate(QString &input, int &pos) const override;
};

/** QTY address widget validator, checks for a valid qty address.
 */
class QTYAddressCheckValidator : public QValidator
{
    Q_OBJECT

public:
    explicit QTYAddressCheckValidator(QObject *parent);

    State validate(QString &input, int &pos) const override;
};

#endif // QTY_QT_QTYADDRESSVALIDATOR_H
